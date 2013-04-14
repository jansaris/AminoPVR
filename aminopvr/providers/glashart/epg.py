"""
    This file is part of AminoPVR.
    Copyright (C) 2012  Ino Dekker

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from StringIO import StringIO
from aminopvr.channel import Channel
from aminopvr.db import DBConnection
from aminopvr.epg import EpgId, EpgProgram, EpgProgramActor, EpgProgramDirector, \
    EpgProgramPresenter, EpgProgramGenre, Genre, Person
from aminopvr.providers.glashart.config import glashartConfig
from aminopvr.scheduler import Scheduler
from aminopvr.timer import Timer
from aminopvr.tools import getPage, Singleton
import datetime
import gzip
import json
import logging
import random
import re
import threading
import time
import unicodedata

_CATTRANS = { "amusement"            : "Talk",
              "animatie"             : "Animated",
              "comedy"               : "Comedy",
              "docu"                 : "Documentary",
              "educatief"            : "Educational",
              "erotiek"              : "Adult",
              "film"                 : "Film",
              "muziek"               : "Art/Music",
              "info"                 : "Educational",
              "jeugd"                : "Children",
              "kunst/cultuur"        : "Arts/Culture",
              "misdaad"              : "Crime/Mystery",
              "muziek"               : "Music",
              "natuur"               : "Science/Nature",
              "actualiteit"          : "News",
              "overige"              : "Unknown",
              "religieus"            : "Religion",
              "serie"                : "Drama",
              "sport"                : "Sports",
              "cultuur"              : "Arts/Culture",
              "wetenschap"           : "Science/Nature" }

def _lineFilter( line ):
    line = unicodedata.normalize( "NFKD", line ).encode( "ASCII", "ignore" )
    return line

class EpgProvider( threading.Thread ):
    __metaclass__ = Singleton

    _logger = logging.getLogger( "aminopvr.providers.glashart.EpgProvider" )

    _timedeltaRegex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')

    def __init__( self ):
        threading.Thread.__init__( self )

        self._logger.debug( "EpgProvider" )

        now          = datetime.datetime.now()
        grabTime     = datetime.datetime.combine( datetime.datetime.today(), datetime.datetime.strptime( glashartConfig.grabEpgTime, "%H:%M" ).timetz() )
        grabInterval = EpgProvider._parseTimedetla( glashartConfig.grabEpgInterval )
        while grabTime < now:
            grabTime = grabTime + grabInterval

        self._logger.warning( "Starting EPG grab timer @ %s with interval %s" % ( grabTime, grabInterval ) )

        self._running = True
        self._event   = threading.Event()
        self._event.clear()

        self._timer = Timer( [ { "time": grabTime, "callback": self._timerCallback, "callbackArguments": None } ], pollInterval=10.0, recurrenceInterval=grabInterval )

    def requestEpgUpdate( self, wait=False ):
        if not self._event.isSet():
            self._event.set()
            if wait:
                while self._event.isSet():
                    time.sleep( 1.0 )
            return True
        else:
            self._logger.warning( "Epg update in progress: skipping request" )
            return False

    def stop( self ):
        self._logger.warning( "Stopping EpgProvider" )
        self._timer.stop()
        self._running = False
        self._event.set()
        self.join()

    def run( self ):
        while self._running:
            self._event.wait()
            if self._running:
                self._grabAll()
                # Request a reschedule
                Scheduler().requestReschedule()
            self._event.clear()

    @staticmethod
    def _parseTimedetla( timeString ):
        parts = EpgProvider._timedeltaRegex.match( timeString )
        if not parts:
            return
        parts      = parts.groupdict()
        timeParams = {}
        for ( name, param ) in parts.iteritems():
            if param:
                timeParams[name] = int( param )
        return datetime.timedelta( **timeParams )

    def _timerCallback( self, event, arguments ):
        if event == Timer.TIME_TRIGGER_EVENT:
            self._logger.warning( "Time to grab EPG." )
            self.requestEpgUpdate( True )

    def _grabAll( self ):
        self._logger.debug( "EpgProvider._grabAll" )

        self._logger.warning( "Grabbing EPG for all channels." )

        self._syncEpgIds()

        db = DBConnection()

        allChannels = Channel.getAllFromDb( db )

        if len( allChannels ) == 0:
            self._logger.critical( "No channels in the database. Script error?" )
            return

        # Get epgids from database (contains channels per epg_id and strategy)
        epgIds = EpgId.getAllFromDb( db )

        now    = time.localtime()
        nowDay = datetime.datetime( now[0], now[1], now[2] )

        # Remove program older than this day
        self._logger.warning( "Removing EPG from before %s" % ( time.mktime( nowDay.timetuple() ) ) )
        EpgProgram.deleteByTimeFromDB( db, int( time.mktime( nowDay.timetuple() ) ) )

        for epgId in epgIds:
            if not self._running:
                break
            self._grabEpgForChannel( epgId=epgId )

        if self._running:
            self._logger.warning( "Grabbing EPG data complete." )
        else:
            self._logger.warning( "Grabbing EPG interrupted." )

    def _grabEpgForChannel( self, channel=None, epgId=None ):
        conn = DBConnection()

        if channel:
            epgId = EpgId.getFromDb( conn, channel.epgId )
            self._logger.info( "Grabbing EPG for channel: %s (%s; method: %s)" % ( channel.name, channel.epgId, epgId.strategy ) )
        if not epgId:
            return
        else:
            self._logger.info( "Grabbing EPG for epgId: %s (method: %s)" % ( epgId.epgId, epgId.strategy ) )

        now             = time.localtime()
        nowDay          = datetime.datetime( now[0], now[1], now[2] )
        daysDetailDelta = datetime.timedelta( days = 3 )

        epgFilename = "/%s.json.gz" % ( epgId.epgId )
        epgUrl      = glashartConfig.epgChannelsPath + epgFilename

        currentPrograms     = EpgProgram.getAllByEpgIdFromDb( conn, epgId.epgId )
        currentProgramsDict = { currProgram.originalId: currProgram for currProgram in currentPrograms }

        content, _, _ = getPage( epgUrl )

        if content:
            fileHandle = gzip.GzipFile( fileobj=StringIO( content ) )
            epgData    = json.loads( fileHandle.read() )

            numPrograms             = 0
            numProgramsDetail       = 0
            numProgramsDetailFailed = 0
            numProgramsNew          = 0
            numProgramsUpdated      = 0

            for program in epgData:
                if not self._running:
                    break

                numPrograms += 1

                programNew = self._getProgramFromJson( epgId.epgId, program )

                updateDetailedData = True

                programOld = None
                if currentProgramsDict.has_key( programNew.originalId ):
                    programOld = currentProgramsDict[programNew.originalId]

                if programOld and programOld.detailed and programNew == programOld:
                    programNew         = programOld
                    updateDetailedData = False

                if updateDetailedData:

                    if ( ( epgId.strategy == "default" and (nowDay + daysDetailDelta) > datetime.datetime.fromtimestamp( programNew.startTime ) ) or
                         ( epgId.strategy == "full" ) ):

                        time.sleep( random.uniform( 0.5, 1.0 ) )

                        programNew, grabbed = self._grabDetailedEpgForProgram( programNew )
                        if grabbed:
                            numProgramsDetail += 1
                        else:
                            # if more than 10 detailed program information grabs failed, set strategy to none.
                            numProgramsDetailFailed += 1
                            if numProgramsDetailFailed == 10:
                                self._logger.error( "Couldn't download at least 10 detailed program information files, so setting strategy to 'none'" )
                                epgId._strategy = "none"
                                epgId.addToDb( conn )

                if not programOld or programNew != programOld:
                    if programOld:
                        self._logger.debug( "Updated program: id = %s" % ( programNew.originalId ) )
                        self._logger.debug( "Start time: %s > %s" % ( str( programOld.startTime ), str( programNew.startTime ) ) )
                        self._logger.debug( "End time:   %s > %s" % ( str( programOld.endTime ),   str( programNew.endTime ) ) )
                        self._logger.debug( "Name:       %s > %s" % ( repr( programOld.title ),    repr( programNew.title ) ) )
                        programNew.id = programOld.id
                        numProgramsUpdated += 1
                    else:
                        numProgramsNew += 1

                    try:
                        programNew.addToDb( conn )
                    except:
                        self._logger.exception( programNew.dump() )

            if self._running:
                self._logger.debug( "Num programs:         %i" % ( numPrograms ) )
                self._logger.debug( "Num program details:  %i" % ( numProgramsDetail ) )
                self._logger.info( "Num new programs:     %i" % ( numProgramsNew ) )
                self._logger.info( "Num updated programs: %i" % ( numProgramsUpdated ) )
                if numProgramsNew == 0:
                    self._logger.warning( "No new programs were added" )
        else:
            self._logger.warning( "Unable to download EPG information for epgId: %s" % ( epgId.epgId ) )

    def _grabDetailedEpgForProgram( self, program, epgId=None ):
        grabbed = True

        # Fetch detailed information. http://w.zt6.nl/epgdata/xx/xxxxxx.json
        detailsFilename   = "/%s/%s.json" % ( program.originalId[-2:], program.originalId )
        detailsUrl        = glashartConfig.epgDataPath + detailsFilename
        detailsPage, _, _ = getPage( detailsUrl, None )

        if detailsPage and len( detailsPage ) > 0:
            detailsData = json.loads( detailsPage )

            program = self._getDetailedProgramFromJson( program, detailsData )
        else:
            grabbed = False

        return program, grabbed

    def _syncEpgIds( self ):
        conn = DBConnection()

        # By not including inactive channels, we automatically delete epgIds that
        # are currently not active
        uniqueEpgIds = Channel.getUniqueEpgIdsFromDb( conn, includeRadio=True )

        # Get epgids from database (contains channels per epg_id and strategy)
        epgIds        = EpgId.getAllFromDb( conn, includeRadio=True )
        epgIdsDict    = { epgId.epgId: epgId for epgId in epgIds }
        currentEpgIds = epgIdsDict.keys()

        for epgId in epgIds:
            if epgId.epgId not in uniqueEpgIds:
                epgId.deleteFromDb( conn )
                self._logger.info( "_syncEpgIds: removing epgId=%s" % ( epgId.epgId ) )

        newEpgIds = set( uniqueEpgIds ).difference( set( currentEpgIds ) )
        self._logger.info( "_syncEpgIds: newEpgIds=%r" % ( newEpgIds ) )

        for newEpgId in newEpgIds:
            epgId = EpgId( newEpgId, "none" )
            epgId.addToDb( conn )
            self._logger.info( "_syncEpgIds: adding epgId=%s" % ( epgId.epgId ) )

    def _getProgramFromJson( self, epgId, json ):
        startTime = json["start"]
        endTime   = json["end"]
        if json.has_key( "name" ):
            title  = _lineFilter( json["name"] )
        else:
            title  = "Onbekend"

        return EpgProgram( epgId, -1, json["id"], startTime, endTime, title )

    def _getDetailedProgramFromJson( self, program, json ):

        if json.has_key( "description" ):
            program.description    = _lineFilter( json["description"] )
        else:
            program.description    = ""

        if json.has_key( "episodeTitle" ):
            program.subtitle       = _lineFilter( json["episodeTitle"] )
        else:
            program.subtitle       = ""

        if json.has_key( "aspectratio" ):
            program.aspectRatio    = _lineFilter( json["aspectratio"] )
        else:
            program.aspectRatio    = ""

        if json.has_key( "nicamParentalRating" ):
            program.parentalRating = _lineFilter( json["nicamParentalRating"] )
        else:
            program.parentalRating = ""

        program.detailed   = True

        program.genres     = self._getAllGenresFromJson( program.id, json )
        program.actors     = self._getAllPersonsFromJson( program.id, json, "actors", EpgProgramActor )
        program.directors  = self._getAllPersonsFromJson( program.id, json, "directors", EpgProgramDirector )
        program.presenters = self._getAllPersonsFromJson( program.id, json, "presenters", EpgProgramPresenter )
        program.ratings    = []

        if json.has_key( "nicamWarning" ):
            rating = json["nicamWarning"]
            if rating & 1:
                program.ratings.append( "angst" )
            if rating & 2:
                program.ratings.append( "seks" )
            if rating & 4:
                program.ratings.append( "geweld" )
            if rating & 8:
                program.ratings.append( "drugs" )
            if rating & 16:
                program.ratings.append( "grof_taalgebruik" )
            if rating & 32:
                program.ratings.append( "discriminatie" )

        # print if there are keys not yet handled by this class
        for key in json.keys():
            if ( key != "start" and key != "end" and key != "id" and key != "name" and
                 key != "description" and key != "episodeTitle" and key != "actors" and
                 key != "directors" and key != "genres" and key != "presenters" and
                 key != "aspectratio" and key != "nicamWarning" and key != "nicamParentalRating" ):
                self._logger.warning( "Unknown json key: %s: %s" % ( key, json[key] ) )

        return program

    def _getGenreFromJson( self, id, json ):
        programGenre = None
        if json:
            genre = _lineFilter( json )

            genreTrans = ""
            if _CATTRANS.has_key( genre.lower() ):
                genreTrans = _CATTRANS[genre.lower()]
            else:
                genreTrans = "GHM - " + genre

            programGenre = EpgProgramGenre( id, -1, Genre( -1, genreTrans ) )

        return programGenre

    def _getAllGenresFromJson( self, id, json ):
        programGenres = []
        if json.has_key( "genres" ):
            for genre in json["genres"]:
                programGenre = self._getGenreFromJson( id, genre )
                if programGenre:
                    programGenres.append( programGenre )
        return programGenres

    def _getPersonFromJson( self, id, json, key, keyClass ):
        programPerson = None
        if json:
            programPerson = keyClass( id, -1, Person( -1, _lineFilter( json ) ) )
        return programPerson

    def _getAllPersonsFromJson( self, id, json, key, keyClass ):
        programPersons = []
        if json.has_key( key ):
            for person in json[key]:
                programPerson = self._getPersonFromJson( id, person, key, keyClass )
                if programPerson:
                    programPersons.append( programPerson )
        return programPersons
