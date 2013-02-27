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
from aminopvr.timer import Timer
from aminopvr.tools import getPage
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

#global_r_entity         = re.compile( r'&(#x[0-9A-Fa-f]+|#[0-9]+|[A-Za-z]+);' )
#global_r_entity_unicode = re.compile( ur'(\\u[0-9A-Fa-f]{4}|\\x[0-9A-Fa-f]{2})', re.UNICODE )
#
#def calc_timezone( t ):
#    """
#    Takes a time from tvgids.nl and formats it with all the required
#    timezone conversions.
#    in: '20050429075000'
#    out:'20050429075000 (CET|CEST)'
#
#    Until I have figured out how to correctly do timezoning in python this method
#    will bork if you are not in a zone that has the same DST rules as 'Europe/Amsterdam'.
#
#    """
#    year   = int( t[0:4] )
#    month  = int( t[4:6] )
#    day    = int( t[6:8] )
#    hour   = int( t[8:10] )
#    minute = int( t[10:12] )
#
#    #td = {'CET': '+0100', 'CEST': '+0200'}
#    #td = {'CET': '+0100', 'CEST': '+0200', 'W. Europe Standard Time' : '+0100', 'West-Europa (standaardtijd)' : '+0100'}
#    td = {0 : '+0100', 1 : '+0200'}
#
#    pt       = time.mktime( ( year, month, day, hour, minute, 0, 0, 0, -1 ) )
#    timezone = ''
#    try:
#        #timezone = time.tzname[(time.localtime(pt))[-1]]
#        timezone = (time.localtime( pt ))[-1]
#    except:
#        sys.stderr.write( 'Cannot convert time to timezone' )
#
#    return t + ' %s' % td[timezone]
#
#def format_timezone( td ):
#    tstr = td.strftime( '%Y%m%d%H%M00' )
#    return calc_timezone( tstr )

#def filter_line_identity( m, defs = htmlentitydefs.entitydefs ):
#    # callback: translate one entity to its ISO Latin value
#    k = m.group(1)
#    if k.startswith( "#" ) and k[1:] in xrange( 256 ):
#        return chr( int( k[1:] ) )
#
#    try:
#        return defs[k]
#    except KeyError:
#        return m.group( 0 ) # use as is
#
#def filter_line_identity_unicode( m, defs = htmlentitydefs.entitydefs ):
#    # callback: translate one entity to its ISO Latin value
#    k = m.group(1)
#    if k.startswith( "\\u" ) or k.startswith( "\\x" ):
#        char_num = int( k[2:], 16 )
#        if char_num in xrange( 256 ):
#            return chr( char_num )
#        else:
#            if char_num == 0x2018 or char_num == 0x2019:
#                return "'"
#            elif char_num == 0x2013:
#                return "-"
#
#    try:
#        return defs[ "x" + k[2:] ]
#    except KeyError:
#        return "" #m.group( 0 ) # use as is

#def filter_line( s, encoding = "iso-8859-1" ):
#    """
#    Removes unwanted stuff in strings (adapted from tv_grab_be)
#    """
#
#    s = s.encode( encoding, 'replace' )
#
#    # do the latin1 stuff
#    s = global_r_entity.sub( filter_line_identity, s )
#    s = global_r_entity_unicode.sub( filter_line_identity_unicode, s )
#
#    s = replace( s, '&nbsp;', ' ' )
#
#    # Ik vermoed dat de volgende drie regels overbodig zijn, maar ze doen
#    # niet veel kwaad -- Han Holl
#    s = replace( s, '\r', ' ' )
#    x = re.compile( '(<.*?>)' ) # Udo
#    s = x.sub( '', s ) #Udo
#
#    s = replace( s, '~Q', "'" )
#    s = replace( s, '~R', "'" )
#
#    return s

#_apostropheRe = re.compile( ur'[\u2018\u2019]', re.UNICODE )
#_dashRe       = re.compile( ur'[\u2013\u2014]', re.UNICODE )
#_dotDotDotRe  = re.compile( ur'[\u2026]',       re.UNICODE )
#_lowerIRe     = re.compile( ur'[\u0131]',       re.UNICODE )
#_upperIRe     = re.compile( ur'[\u0130]',       re.UNICODE )
#_lowerGRe     = re.compile( ur'[\u011F]',       re.UNICODE )
#_lowerSRe     = re.compile( ur'[\u015F]',       re.UNICODE )
#_upperSRe     = re.compile( ur'[\u015E]',       re.UNICODE )
#_euroRe       = re.compile( ur'[\u20AC]',       re.UNICODE )
#_aRe          = re.compile( ur'[\xe2]',         re.UNICODE )
#_eRe          = re.compile( ur'[\xe9]',         re.UNICODE )
#_uRe          = re.compile( ur'[\xfc]',         re.UNICODE )

def _lineFilter( line ):
#    _logger.debug( "_lineFilter( %r )" % ( line ) )
    line = unicodedata.normalize( "NFKD", line ).encode( "ASCII", "ignore" )
##    line = global_r_entity_unicode.sub( filter_line_identity_unicode, line )
#    line = _apostropheRe.sub( "'", line )
#    line = _dashRe.sub( "-", line )
#    line = _dotDotDotRe.sub( "...", line )
#    line = _lowerIRe.sub( "i", line )
#    line = _upperIRe.sub( "I", line )
#    line = _lowerGRe.sub( "g", line )
#    line = _lowerSRe.sub( "s", line )
#    line = _upperSRe.sub( "S", line )
#    line = _euroRe.sub( "E", line )
#    line = _aRe.sub( "a", line )
#    line = _eRe.sub( "e", line )
#    line = _uRe.sub( "u", line )
    return line

class EpgProvider( threading.Thread ):
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

        self._timer = Timer( [ { "time": grabTime, "callback": self._timerCallback, "callbackArguments": None } ], recurrenceInterval=grabInterval )

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
        self._logger.debug( "grabAll" )

        self._logger.info( "Grabbing EPG for all channels." )

        self._syncEpgIds()

        db = DBConnection()

        allChannels = Channel.getAllFromDb( db )

        if len( allChannels ) == 0:
            self._logger.critical( "No channels parsed from index page. Script error?" )
            return

        # Get epgids from database (contains channels per epg_id and strategy)
        epgIds = EpgId.getAllFromDb( db )

        now    = time.localtime()
        nowDay = datetime.datetime( now[0], now[1], now[2] )

        # Remove program older than this day
        self._logger.info( "Removing EPG from before %i" % ( int( time.mktime( nowDay.timetuple() ) ) ) )
        EpgProgram.deleteByTimeFromDB( db, int( time.mktime( nowDay.timetuple() ) ) )

        for epgId in epgIds:
            if not self._running:
                break
            self._grabEpgForChannel( epgId=epgId )

        if self._running:
            self._logger.info( "Grabbing EPG data complete." )

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

        content, code, mime = getPage( epgUrl )

        if content:
            fileHandle = gzip.GzipFile( fileobj=StringIO( content ) )
            epgData    = json.loads( fileHandle.read() )

            numPrograms             = 0
            numProgramsDetail       = 0
            numProgramsDetailFailed = 0

            for program in epgData:
                if not self._running:
                    break

                numPrograms += 1

                programNew = self._getProgramFromJson( epgId.epgId, program )

                updateDetailedData = True

                programOld = EpgProgram.getByOriginalIdFromDb( conn, programNew.originalId )

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
                        self._logger.info( "Updated program: id = %s" % ( programNew.originalId ) )
                        self._logger.info( "Start time: %s > %s" % ( str( programOld.startTime ), str( programNew.startTime ) ) )
                        self._logger.info( "End time:   %s > %s" % ( str( programOld.endTime ),   str( programNew.endTime ) ) )
                        self._logger.info( "Name:       %s > %s" % ( repr( programOld.title ),    repr( programNew.title ) ) )

                    try:
                        programNew.addToDb( conn )
                    except:
                        self._logger.exception( programNew.dump() )

            if self._running:
                self._logger.info( "Num programs:        %i" % numPrograms )
                self._logger.info( "Num program details: %i" % numProgramsDetail )
        else:
            self._logger.warning( "Unable to download EPG information for epgId: %s" % ( epgId.epgId ) )

    def _grabDetailedEpgForProgram( self, program, epgId=None ):
        grabbed = True

        # Fetch detailed information. http://w.zt6.nl/epgdata/xx/xxxxxx.json
        detailsFilename         = "/%s/%s.json" % ( program.originalId[-2:], program.originalId )
        detailsUrl              = glashartConfig.epgDataPath + detailsFilename
        detailsPage, code, mime = getPage( detailsUrl, None )

        if detailsPage and len( detailsPage ) > 0:
            detailsData = json.loads( detailsPage )

            program = self._getDetailedProgramFromJson( program, detailsData )
        else:
            grabbed = False

        return program, grabbed

    def _syncEpgIds( self ):
        """
        TODO: 'disable' epgIds when no channels are active with this epgId
        """
        conn = DBConnection()

        uniqueEpgIds = Channel.getUniqueEpgIdsFromDb( conn )

        # Get epgids from database (contains channels per epg_id and strategy)
        epgIds        = EpgId.getAllFromDb( conn )
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
