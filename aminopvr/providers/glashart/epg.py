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
from aminopvr.database.channel import Channel
from aminopvr.config import Config
from aminopvr.database.db import DBConnection
from aminopvr.database.epg import EpgId, EpgProgram, EpgProgramActor, EpgProgramDirector, \
    EpgProgramPresenter, EpgProgramGenre, Genre, Person
from aminopvr.providers.glashart.config import GlashartConfig
from aminopvr.scheduler import Scheduler
from aminopvr.timer import Timer
from aminopvr.tools import getPage, Singleton, getTimestamp, \
    parseTimedetlaString
import datetime
import gzip
import json
import logging
import random
import re
import sys
import threading
import time
import unicodedata

# Content_nibble_level_1 Content_nibble_level_2 Description
# 0x0 0x0 to 0xF undefined content
# Movie/Drama:
# 0x1 0x0 movie/drama (general)
# 0x1 0x1 detective/thriller
# 0x1 0x2 adventure/western/war
# 0x1 0x3 science fiction/fantasy/horror
# 0x1 0x4 comedy
# 0x1 0x5 soap/melodrama/folkloric
# 0x1 0x6 romance
# 0x1 0x7 serious/classical/religious/historical movie/drama
# 0x1 0x8 adult movie/drama
# 0x1 0x9 to 0xE reserved for future use
# 0x1 0xF user defined
# News/Current affairs:
# 0x2 0x0 news/current affairs (general)
# 0x2 0x1 news/weather report
# 0x2 0x2 news magazine
# 0x2 0x3 documentary
# 0x2 0x4 discussion/interview/debate
# 0x2 0x5 to 0xE reserved for future use
# 0x2 0xF user defined
# Show/Game show:
# 0x3 0x0 show/game show (general)
# 0x3 0x1 game show/quiz/contest
# 0x3 0x2 variety show
# 0x3 0x3 talk show
# 0x3 0x4 to 0xE reserved for future use
# 0x3 0xF user defined
# Sports:
# 0x4 0x0 sports (general) 
# 0x4 0x1 special events (Olympic Games, World Cup, etc.)
# 0x4 0x2 sports magazines
# 0x4 0x3 football/soccer
# 0x4 0x4 tennis/squash
# 0x4 0x5 team sports (excluding football)
# 0x4 0x6 athletics
# 0x4 0x7 motor sport
# 0x4 0x8 water sport
# 0x4 0x9 winter sports

_CATTRANS = { "talk"                 : "Talk",
              "amusement"            : "Talk",
              "animatie"             : "Animated",
              "comedy"               : "Comedy",
              "documentary"          : "Documentary",
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
              "other"                : "Unknown",
              "overige"              : "Unknown",
              "unknown"              : "Unknown",
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

    _logger         = logging.getLogger( "aminopvr.providers.glashart.EpgProvider" )

    def __init__( self ):
        threading.Thread.__init__( self )

        self._logger.debug( "EpgProvider" )

        self._glashartConfig = GlashartConfig( Config() )

        now          = datetime.datetime.now()
        grabTime     = datetime.datetime.combine( datetime.datetime.today(), datetime.datetime.strptime( self._glashartConfig.grabEpgTime, "%H:%M" ).timetz() )
        grabInterval = parseTimedetlaString( self._glashartConfig.grabEpgInterval )
        while grabTime < now:
            grabTime = grabTime + grabInterval

        self._logger.warning( "Starting EPG grab timer @ %s with interval %s" % ( grabTime, grabInterval ) )

        self._lastUpdate    = 0
        self._running       = True
        self._event         = threading.Event()
        self._event.clear()

        self._timer = Timer( [ { "time": grabTime, "callback": self._timerCallback, "callbackArguments": None } ], pollInterval=10.0, recurrenceInterval=grabInterval )

        if not self._haveEnoughEpgData():
            self._logger.warning( "Not enough Epg data in database. Request Epg update." )
            self.requestEpgUpdate()

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

    def getLastUpdate( self ):
        return self._lastUpdate;

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
                try:
                    self._grabAll()
                    self._lastUpdate = getTimestamp()
                    if not self._haveEnoughEpgData():
                        self._logger.warning( "Updated Epg, but there is still not enough data available.")
                except:
                    self._logger.error( "run: unexcepted error: %s" % ( sys.exc_info()[0] ) )
                # Request a reschedule
                Scheduler().requestReschedule()
            self._event.clear()

    def _haveEnoughEpgData( self ):
        conn        = DBConnection()
        lastProgram = EpgProgram.getTimestampLastProgram( conn )
        timestamp   = getTimestamp()
        if timestamp < lastProgram:
            daysLeft = float(lastProgram - timestamp) / (24 * 60 * 60)
            self._logger.warning( "Currently %.1f days of Epg data in database." % ( daysLeft ) )
        if timestamp + (24 * 60 * 60) > lastProgram:
            return False
        return True

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
        self._logger.warning( "Removing EPG from before %s" % ( getTimestamp( nowDay ) ) )
        EpgProgram.deleteByTimeFromDB( db, getTimestamp( nowDay ) )

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

        # Check if _fail_# is behind strategy
        # This is to indicate epg grabbing for this epgId failed previously
        strategy   = epgId.strategy
        strategyRe = re.compile( r'_fail_(?P<fail>\d+)' )
        failMatch  = strategyRe.search( strategy )
        failCount  = 0
        if failMatch:
            failCount = int( failMatch.group( "fail" ) )
            strategy  = epgId.strategy.split( '_' )[0]

        # We're going to attempt to grab EPG information for this channel 5 times
        # before we stop grabbing this epgId in the future.
        if failCount < 5:
            now             = time.localtime()
            nowDay          = datetime.datetime( now[0], now[1], now[2] )
            daysDetailDelta = datetime.timedelta( days = 3 )

            epgFilename = "/%s.json.gz" % ( epgId.epgId )
            epgUrl      = self._glashartConfig.epgChannelsPath + epgFilename

            currentPrograms     = EpgProgram.getAllByEpgIdFromDb( conn, epgId.epgId )
            currentProgramsDict = { currProgram.originalId: currProgram for currProgram in currentPrograms }
            newProgramsDict     = {}

            content, _, _ = getPage( epgUrl )

            if content:
                fileHandle = gzip.GzipFile( fileobj=StringIO( content ) )
                epgData    = json.loads( fileHandle.read() )

                # If strategy has changed (working after (a few) failed attempts)
                if epgId.strategy != strategy:
                    epgId.strategy = strategy
                    epgId.addToDb( conn )

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
                    if programNew.originalId in newProgramsDict:
                        self._logger.warning( "Program with originalId %d already in newProgramsDict" % ( programNew.originalId ) )
                    newProgramsDict[programNew.originalId] = programNew

                    updateDetailedData = True

                    programOld = None
                    if programNew.originalId in currentProgramsDict:
                        programOld = currentProgramsDict[programNew.originalId]

                    # If the old program has detailed info, copy those fields
                    # TODO: do this somewhere else
                    if programOld and programOld.detailed:
                        programNew.subtitle       = programOld.subtitle
                        programNew.description    = programOld.description
                        programNew.aspectRatio    = programOld.aspectRatio
                        programNew.parentalRating = programOld.parentalRating
                        programNew.genres         = programOld.genres
                        programNew.actors         = programOld.actors
                        programNew.directors      = programOld.directors
                        programNew.presenters     = programOld.presenters
                        programNew.ratings        = programOld.ratings
                        programNew.detailed       = programOld.detailed

                    # Now, compare the old program and the new program
                    # Are they the same, then we don't need to download detailed information
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
                                    self._logger.error( "Couldn't download at least 10 detailed program information files, so setting strategy to 'none', but do not store" )
                                    epgId.strategy = "none"

                conn.delayCommit( True )

                for programId in newProgramsDict:
                    programNew = newProgramsDict[programId]
                    programOld = None
                    if programNew.originalId in currentProgramsDict:
                        programOld = currentProgramsDict[programNew.originalId]

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

                conn.delayCommit( False )

                if self._running:
                    self._logger.debug( "Num programs:         %i" % ( numPrograms ) )
                    self._logger.debug( "Num program details:  %i" % ( numProgramsDetail ) )
                    self._logger.info( "Num new programs:     %i" % ( numProgramsNew ) )
                    self._logger.info( "Num updated programs: %i" % ( numProgramsUpdated ) )
                    if numProgramsNew == 0:
                        self._logger.warning( "No new programs were added for epgId: %s" % ( epgId.epgId ) )
            else:
                self._logger.warning( "Unable to download EPG information for epgId: %s" % ( epgId.epgId ) )
                failCount     += 1
                epgId.strategy = "%s_fail_%d" % ( strategy, failCount )
                epgId.addToDb( conn )
        else:
            self._logger.info( "Downloading of EPG information for epgId: %s skipped becaused it failed too many times" % ( epgId.epgId ) )

    def _grabDetailedEpgForProgram( self, program, epgId=None ):
        grabbed = True

        # Fetch detailed information. http://w.zt6.nl/epgdata/xx/xxxxxx.json
        detailsFilename   = "/%s/%s.json" % ( program.originalId[-2:], program.originalId )
        detailsUrl        = self._glashartConfig.epgDataPath + detailsFilename
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

        program             = EpgProgram()
        program.epgId       = epgId
        program.originalId  = json["id"]
        program.startTime   = startTime
        program.endTime     = endTime
        program.title       = title

        return program

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
            if key not in ["start", "end", "id", "name", "description", "episodeTitle", "actors",
                           "directors", "genres", "presenters", "aspectratio", "nicamWarning",
                           "nicamParentalRating", "disableRestart", "restartPriceTier"]:
                self._logger.warning( "Unknown json key: %s: %s" % ( key, json[key] ) )

        return program

    def _getGenreFromJson( self, id, json ):  # @ReservedAssignment
        programGenre = None
        if json:
            genre = _lineFilter( json )

            genreTrans = ""
            if _CATTRANS.has_key( genre.lower() ):
                genreTrans = _CATTRANS[genre.lower()]
            else:
                genreTrans = "GHM - " + genre

            genre               = Genre()
            genre.genre         = genreTrans

            programGenre        = EpgProgramGenre( id, -1 )
            programGenre.genre  = genre

        return programGenre

    def _getAllGenresFromJson( self, id_, json ):
        programGenres = []
        if json.has_key( "genres" ):
            for genre in json["genres"]:
                programGenre = self._getGenreFromJson( id_, genre )
                if programGenre:
                    programGenres.append( programGenre )
        return programGenres

    def _getPersonFromJson( self, id_, json, key, keyClass ):
        programPerson = None
        if json:
            person                  = Person()
            person.person           = _lineFilter( json )
            programPerson           = keyClass( id_ )
            programPerson.person    = person
        return programPerson

    def _getAllPersonsFromJson( self, id_, json, key, keyClass ):
        programPersons = []
        if json.has_key( key ):
            for person in json[key]:
                programPerson = self._getPersonFromJson( id_, person, key, keyClass )
                if programPerson:
                    programPersons.append( programPerson )
        return programPersons
