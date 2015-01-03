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
from aminopvr.config import Config, GeneralConfig
from aminopvr.database.channel import Channel, ChannelUrl
from aminopvr.database.db import DBConnection
from aminopvr.database.epg import RecordingProgram, Genre, RecordingProgramGenre
from aminopvr.database.recording import Recording, RecordingState, OldRecording
from aminopvr.resource_monitor import ResourceMonitor
from aminopvr.database.schedule import Schedule
from aminopvr.tools import getTimestamp
from shutil import copyfile
import MySQLdb
import aminopvr
import datetime
import getopt
import logging
import os
import re
import sys
import threading
import traceback

class CustomFormatter( logging.Formatter ):
    width = 16

    def __init__( self, default ):
        self._default = default

    def format( self, record ):
        if len( record.name ) > self.width:
            record.name = record.name[-self.width:]
        return self._default.format( record )

def formatFactory( fmt, datefmt ):
    default = logging.Formatter( fmt, datefmt )
    return CustomFormatter( default )

formatter = CustomFormatter( logging.Formatter( "%(asctime)s <%(levelname).1s> %(name)16s[%(lineno)4d]: %(message)s", "%Y%m%d %H:%M:%S" ) )

consoleHandler = logging.StreamHandler( sys.stdout )
consoleHandler.setLevel( logging.INFO )
consoleHandler.setFormatter( formatter )

logger = logging.getLogger( "aminopvr" )
logger.setLevel( logging.WARNING )
logger.addHandler( consoleHandler )

_CATTRANS = { "animated"             : "Animated",
              "animatie"             : "Animated",
              "adult"                : "Adult",
              "erotiek"              : "Adult",
              "art/music"            : "Art/Music",
              "muziek"               : "Art/Music",
              "art/culture"          : "Arts/Culture",
              "cultuur"              : "Arts/Culture",
              "kunst/cultuur"        : "Arts/Culture",
              "children"             : "Children",
              "jeugd"                : "Children",
              "comedy"               : "Comedy",
              "crime/mystery"        : "Crime/Mystery",
              "misdaad"              : "Crime/Mystery",
              "documentary"          : "Documentary",
              "docu"                 : "Documentary",
              "drama"                : "Drama",
              "serie"                : "Drama",
              "educatief"            : "Educational",
              "educational"          : "Educational",
              "info"                 : "Educational",
              "film"                 : "Film",
              "music"                : "Music",
              "muziek"               : "Music",
              "actualiteit"          : "News",
              "news"                 : "News",
              "religieus"            : "Religion",
              "religion"             : "Religion",
              "natuur"               : "Science/Nature",
              "science/nature"       : "Science/Nature",
              "wetenschap"           : "Science/Nature",
              "sport"                : "Sports",
              "sports"               : "Sports",
              "amusement"            : "Talk",
              "talk"                 : "Talk",
              "other"                : "Unknown",
              "overige"              : "Unknown",
              "unknown"              : "Unknown" }

class MythTvChannel( object ):

    _logger = logging.getLogger( "aminopvr.MytvTvChannel" )

    def __init__( self, chanid, channum, callsign, name, xmltvid, icon ):
        self._chanid     = int( chanid )
        self._channum    = int( channum )
        self._callsign   = unicode( callsign )
        self._name       = unicode( name )
        self._xmltvid    = unicode( xmltvid )
        self._icon       = unicode( icon )

    def __eq__( self, other ):
        return ( self._chanid   != other._chanid   and
                 self._channum  != other._channum  and
                 self._callsign != other._callsign and
                 self._name     != other._name     and
                 self._xmltvid  != other._xmltvid  and
                 self._icon     != other._icon )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @property
    def chanId( self ):
        return self._chanid

    @property
    def chanNum( self ):
        return self._channum

    @property
    def callsign( self ):
        return self._callsign

    @property
    def name( self ):
        return self._name

    @property
    def xmlTvId( self ):
        return self._xmltvid

    @property
    def icon( self ):
        return self._icon

    @classmethod
    def getAllByEpgIdFromDb( cls, conn, xmltvid ):
        channels = []
        if conn:
            cursor = conn.cursor( MySQLdb.cursors.DictCursor )
            cursor.execute( "SELECT * FROM channel WHERE xmltvid=%s", ( xmltvid ) )
            rows = cursor.fetchall()
            for row in rows:
                channel = cls._createMytvTvChannelObjectFromDbDict( row )
                channels.append( channel )

        return channels

    @classmethod
    def getAllFromDb( cls, conn ):
        channels = []
        if conn:
            cursor = conn.cursor( MySQLdb.cursors.DictCursor )
            cursor.execute( "SELECT * FROM channel" )
            rows = cursor.fetchall()
            for row in rows:
                channel = cls._createMytvTvChannelObjectFromDbDict( row )
                channels.append( channel )

        return channels

    @classmethod
    def getByChanIdFromDb( cls, conn, chanid ):
        channel = None
        if conn:
            cursor = conn.cursor( MySQLdb.cursors.DictCursor )
            cursor.execute( "SELECT * FROM channel WHERE chanid=%s", ( chanid ) )
            channel = cls._createMytvTvChannelObjectFromDbDict( cursor.fetchone() )
        return channel

    @classmethod
    def getByChanNumFromDb( cls, conn, channum ):
        channel = None
        if conn:
            cursor = conn.cursor( MySQLdb.cursors.DictCursor )
            cursor.execute( "SELECT * FROM channel WHERE channum=%s", ( channum ) )
            channel = cls._createMytvTvChannelObjectFromDbDict( cursor.fetchone() )
        return channel

    @classmethod
    def _createMytvTvChannelObjectFromDbDict( cls, channelData ):
        channel = None
        if channelData:
            channel = cls( channelData["chanid"],
                           channelData["channum"],
                           channelData["callsign"],
                           channelData["name"],
                           channelData["xmltvid"],
                           channelData["icon"] )
        return channel

    def dump( self ):
        return ( "%i (%i): %s (%s, %s)" % ( self._chanid, self._channum, self._name, self._callsign, self._xmltvid ) )

class MythTvIptvChannel( object ):

    _logger = logging.getLogger( "aminopvr.MytvTvIptvChannel" )

    def __init__( self, chanid, url ):
        self._chanid = int( chanid )
        self._url    = unicode( url )

    def __eq__( self, other ):
        return ( self._chanid != other._chanid and
                 self._url    != other._url )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @property
    def chanId( self ):
        return self._chanid

    @property
    def url( self ):
        return self._url

    @classmethod
    def getAllFromDb( cls, conn ):
        channels = []
        if conn:
            cursor = conn.cursor( MySQLdb.cursors.DictCursor )
            cursor.execute( "SELECT * FROM iptv_channel" )
            rows = cursor.fetchall()
            for row in rows:
                channel = cls._createMytvTvIptvChannelObjectFromDbDict( row )
                channels.append( channel )

        return channels

    @classmethod
    def getByChanIdFromDb( cls, conn, chanid ):
        channel = None
        if conn:
            cursor = conn.cursor( MySQLdb.cursors.DictCursor )
            cursor.execute( "SELECT * FROM iptv_channel WHERE chanid=%s", ( chanid ) )
            channel = cls._createMytvTvIptvChannelObjectFromDbDict( cursor.fetchone() )
        return channel

    @classmethod
    def _createMytvTvIptvChannelObjectFromDbDict( cls, channelData ):
        channel = None
        if channelData:
            channel = cls( channelData["chanid"],
                           channelData["url"] )
        return channel

    def dump( self ):
        return ( "%i: %s" % ( self._chanid, self._url ) )

class MythTvRecord( object ):

    _logger = logging.getLogger( "aminopvr.MytvTvRecord" )

    def __init__( self, recordid, type, chanid, starttime, endtime, title, dupmethod, startoffset, endoffset, inactive ):
        self._recordid    = int( recordid )
        self._type        = int( type )
        self._chanid      = int( chanid )
        self._starttime   = int( starttime )
        self._endtime     = int( endtime )
        self._title       = unicode( title )
        self._dupmethod   = int( dupmethod )
        self._startoffset = int( startoffset )
        self._endoffset   = int( endoffset )
        self._inactive    = int( inactive )

    def __eq__( self, other ):
        return ( self._recordid    != other._recordid    and
                 self._type        != other._type        and
                 self._chanid      != other._chanid      and
                 self._starttime   != other._starttime   and
                 self._endtime     != other._endtime     and
                 self._title       != other._title       and
                 self._dupmethod   != other._dupmethod   and
                 self._startoffset != other._startoffset and
                 self._endoffset   != other._endoffset   and
                 self._inactive    != other._inactive )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @property
    def recordId( self ):
        return self._recordid

    @property
    def type( self ):
        return self._type

    @property
    def chanId( self ):
        return self._chanid

    @property
    def startTime( self ):
        return self._starttime

    @property
    def endTime( self ):
        return self._endtime

    @property
    def title( self ):
        return self._title

    @property
    def dupMethod( self ):
        return self._dupmethod

    @property
    def startOffset( self ):
        return self._startoffset

    @property
    def endOffset( self ):
        return self._endoffset

    @property
    def inactive( self ):
        return self._inactive

    @classmethod
    def getAllFromDb( cls, conn ):
        records = []
        if conn:
            cursor = conn.cursor( MySQLdb.cursors.DictCursor )
            cursor.execute( "SELECT * FROM record" )
            rows = cursor.fetchall()
            for row in rows:
                record = cls._createMytvTvRecordObjectFromDbDict( row )
                records.append( record )

        return records

    @classmethod
    def _createMytvTvRecordObjectFromDbDict( cls, recordData ):
        record = None
        if recordData:
            record = cls( recordData["recordid"],
                          recordData["type"],
                          recordData["chanid"],
                          getTimestamp( datetime.datetime.combine( recordData["startdate"], datetime.time.min ) + recordData["starttime"] ),
                          getTimestamp( datetime.datetime.combine( recordData["enddate"], datetime.time.min )   + recordData["endtime"] ),
                          recordData["title"],
                          recordData["dupmethod"],
                          recordData["startoffset"] * 60,
                          recordData["endoffset"] * 60,
                          recordData["inactive"] )
        return record

    def dump( self ):
        return ( "%i (%i): %i (%i-%i) %s (%i, %i, %i, %i)" % ( self._recordid, self._type, self._chanid, self._starttime, self._endtime, self._title, self._dupmethod, self._startoffset, self._endoffset, self._inactive ) )

class MythTvRecorded( object ):

    _logger = logging.getLogger( "aminopvr.MytvTvRecorded" )

    def __init__( self, recordid, chanid, starttime, endtime, title, basename, filesize, progstart, progend ):
        self._recordid    = int( recordid )
        self._chanid      = int( chanid )
        self._starttime   = int( starttime )
        self._endtime     = int( endtime )
        self._title       = unicode( title )
        self._basename    = unicode( basename )
        self._filesize    = int( filesize )
        self._progstart   = int( progstart )
        self._progend     = int( progend )

    def __eq__( self, other ):
        return ( self._recordid    != other._recordid    and
                 self._chanid      != other._chanid      and
                 self._starttime   != other._starttime   and
                 self._endtime     != other._endtime     and
                 self._title       != other._title       and
                 self._basename    != other._basename    and
                 self._filesize    != other._filesize    and
                 self._progstart   != other._progstart   and
                 self._progend     != other._progend )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @property
    def recordId( self ):
        return self._recordid

    @property
    def chanId( self ):
        return self._chanid

    @property
    def startTime( self ):
        return self._starttime

    @property
    def endTime( self ):
        return self._endtime

    @property
    def title( self ):
        return self._title

    @property
    def baseName( self ):
        return self._basename

    @property
    def fileSize( self ):
        return self._filesize

    @property
    def programStart( self ):
        return self._progstart

    @property
    def programEnd( self ):
        return self._progend

    @classmethod
    def getAllFromDb( cls, conn ):
        records = []
        if conn:
            cursor = conn.cursor( MySQLdb.cursors.DictCursor )
            cursor.execute( "SELECT * FROM recorded" )
            rows = cursor.fetchall()
            for row in rows:
                record = cls._createMytvTvRecordedObjectFromDbDict( row )
                records.append( record )

        return records

    @classmethod
    def _createMytvTvRecordedObjectFromDbDict( cls, recordedData ):
        recorded = None
        if recordedData:
            recorded = cls( recordedData["recordid"],
                            recordedData["chanid"],
                            getTimestamp( recordedData["starttime"] ),
                            getTimestamp( recordedData["endtime"] ),
                            recordedData["title"],
                            recordedData["basename"],
                            recordedData["filesize"],
                            getTimestamp( recordedData["progstart"] ),
                            getTimestamp( recordedData["progend"] ) )
        return recorded

    def dump( self ):
        return ( "%i (%i): (%i-%i) %s (%s (%i), (%i-%i)" % ( self._recordid, self._chanid, self._starttime, self._endtime, self._title, self._basename, self._filesize, self._progstart, self._progend ) )

class MythTvOldRecorded( object ):

    _logger = logging.getLogger( "aminopvr.MytvTvOldRecorded" )

    def __init__( self, recordid, chanid, starttime, endtime, title, subtitle, description, category ):
        self._recordid    = int( recordid )
        self._chanid      = int( chanid )
        self._starttime   = int( starttime )
        self._endtime     = int( endtime )
        self._title       = unicode( title )
        self._subtitle    = unicode( subtitle )
        self._description = unicode( description )
        self._category    = unicode( category )

    def __eq__( self, other ):
        return ( self._recordid    != other._recordid    and
                 self._chanid      != other._chanid      and
                 self._starttime   != other._starttime   and
                 self._endtime     != other._endtime     and
                 self._title       != other._title       and
                 self._subtitle    != other._subtitle    and
                 self._description != other._description and
                 self._category    != other._category )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @property
    def recordId( self ):
        return self._recordid

    @property
    def chanId( self ):
        return self._chanid

    @property
    def startTime( self ):
        return self._starttime

    @property
    def endTime( self ):
        return self._endtime

    @property
    def title( self ):
        return self._title

    @property
    def subtitle( self ):
        return self._subtitle

    @property
    def description( self ):
        return self._description

    @property
    def category( self ):
        return self._category

    @classmethod
    def getAllFromDb( cls, conn ):
        records = []
        if conn:
            cursor = conn.cursor( MySQLdb.cursors.DictCursor )
            cursor.execute( "SELECT * FROM oldrecorded WHERE recstatus=-3" )
            rows = cursor.fetchall()
            for row in rows:
                record = cls._createMytvTvOldRecordedObjectFromDbDict( row )
                records.append( record )

        return records

    @classmethod
    def _createMytvTvOldRecordedObjectFromDbDict( cls, recordedData ):
        recorded = None
        if recordedData:
            recorded = cls( recordedData["recordid"],
                            recordedData["chanid"],
                            getTimestamp( recordedData["starttime"] ),
                            getTimestamp( recordedData["endtime"] ),
                            recordedData["title"],
                            recordedData["subtitle"],
                            recordedData["description"],
                            recordedData["category"] )
        return recorded

    def dump( self ):
        return ( "%i (%i): (%i-%i) %s:%s (%s, %s)" % ( self._recordid, self._chanid, self._starttime, self._endtime, self._title, self._subtitle, self._description, self._category ) )

class MythTvRecordedProgram( object ):

    _logger = logging.getLogger( "aminopvr.MytvTvRecordedProgram" )

    def __init__( self, chanid, starttime, endtime, title, subtitle, description, category ):
        self._chanid      = int( chanid )
        self._starttime   = int( starttime )
        self._endtime     = int( endtime )
        self._title       = unicode( title )
        self._subtitle    = unicode( subtitle )
        self._description = unicode( description )
        self._category    = unicode( category )

    def __eq__( self, other ):
        return ( self._chanid      != other._chanid      and
                 self._starttime   != other._starttime   and
                 self._endtime     != other._endtime     and
                 self._title       != other._title       and
                 self._subtitle    != other._subtitle    and
                 self._description != other._description and
                 self._category    != other._category )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @property
    def chanId( self ):
        return self._chanid

    @property
    def startTime( self ):
        return self._starttime

    @property
    def endTime( self ):
        return self._endtime

    @property
    def title( self ):
        return self._title

    @property
    def subtitle( self ):
        return self._subtitle

    @property
    def description( self ):
        return self._description

    @property
    def category( self ):
        return self._category

    @classmethod
    def getAllFromDb( cls, conn ):
        records = []
        if conn:
            cursor = conn.cursor( MySQLdb.cursors.DictCursor )
            cursor.execute( "SELECT * FROM recordedprogram" )
            rows = cursor.fetchall()
            for row in rows:
                record = cls._createMytvTvRecordedProgramObjectFromDbDict( row )
                records.append( record )

        return records

    @classmethod
    def _createMytvTvRecordedProgramObjectFromDbDict( cls, recordedData ):
        recorded = None
        if recordedData:
            recorded = cls( recordedData["chanid"],
                            getTimestamp( recordedData["starttime"] ),
                            getTimestamp( recordedData["endtime"] ),
                            recordedData["title"],
                            recordedData["subtitle"],
                            recordedData["description"],
                            recordedData["category"] )
        return recorded

    def dump( self ):
        return ( "%i: (%i-%i) %s:%s (%s, %s)" % ( self._chanid, self._starttime, self._endtime, self._title, self._subtitle, self._category, self._description ) )

def _addChannel( chanId, mythTvChannelsDict, mythTvIptvChannelsDict, dryRun ):
    channel = None
    urlType = None

    if chanId in mythTvChannelsDict:
        mythTvChannel = mythTvChannelsDict[chanId]
        if chanId in mythTvIptvChannelsDict:
            mythTvIptvChannel = mythTvIptvChannelsDict[chanId]

            urlRe    = re.compile( r"(?P<protocol>[a-z]{3,5}):\/\/(?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}):(?P<port>[0-9]{1,5})" )
            urlMatch = urlRe.search( mythTvIptvChannel.url )
            if urlMatch:
                urlType   = u"sd"
                protocol  = "igmp"
                ip        = urlMatch.group( "ip" )
                port      = int( urlMatch.group( "port" ) )
                arguments = ""
                if urlMatch.group( "protocol" ) == "rtp":
                    arguments = ";rtpskip=yes"

                channel                 = Channel()
                channel.number          = mythTvChannel.chanNum
                channel.epgId           = mythTvChannel.xmlTvId
                channel.name            = mythTvChannel.name
                channel.nameShort       = mythTvChannel.callsign
                channel.inactive        = True

                channelUrl              = ChannelUrl( urlType )
                channelUrl.protocol     = protocol
                channelUrl.ip           = ip
                channelUrl.port         = port
                channelUrl.arguments    = arguments
                channelUrl.scrambled    = False

                channel.urls[urlType]   = channelUrl

                _copyLogoAndThumbnail( channel, mythTvChannel, dryRun )
    else:
        logger.warning( "channel with chanId=%i not found in mythTvChannelsDict" % ( chanId ) )

    return ( channel, urlType )

def _copyLogoAndThumbnail( channel, mythtvChannel, dryRun ):
    if mythtvChannel.icon != "":
        icon           = channel.epgId + ".png"
        logoPath       = os.path.join( aminopvr.const.DATA_ROOT, "assets/images/channels/logos", icon )
        if not os.path.exists( logoPath ):
            channel.logo = icon
            if not dryRun:
                copyfile( mythtvChannel.icon, logoPath )
            logger.warning( "_copyLogoAndThumbnail: copied logo to %s" % ( logoPath ) )
        thumbnailPath  = os.path.join( aminopvr.const.DATA_ROOT, "assets/images/channels/thumbnails", icon )
        if not os.path.exists( thumbnailPath ):
            channel.thumbnail = icon
            if not dryRun:
                copyfile( mythtvChannel.icon, thumbnailPath )
            logger.warning( "_copyLogoAndThumbnail: copied thumbnail to %s" % ( thumbnailPath ) )

def main():
    aminopvr.const.DATA_ROOT = os.path.dirname( os.path.abspath( __file__ ) )

    # Rename the main thread
    threading.currentThread().name = "MAIN"

    generalConfig = GeneralConfig( Config() )

    dryRun          = True
    mysqlHost       = "localhost"
    mysqlDb         = "mythconverg"
    mysqlUser       = "mythtv"
    mysqlPass       = ""
    mythtvRecPath   = "."

    try:
        opts, args = getopt.getopt( sys.argv[1:], "cv", ['commit', 'verbose', 'host=', 'user=', 'pass=', 'db=', 'mythrec='] )  # @UnusedVariable
    except getopt.GetoptError:
        print "Available Options: --commit, --verbose, --host=<hostname>, --user=<username>, --pass=<password>, --db=<database>, --mythrec=<path>"
        sys.exit()

    for o, a in opts:
        if o in ( '-v', '--verbose' ):
            logger.setLevel( logging.DEBUG )

        if o in ( '-c', '--commit' ):
            dryRun = False

        if o in ( '--host', ):
            mysqlHost = str( a )

        if o in ( '--user', ):
            mysqlUser = str( a )

        if o in ( '--pass', ):
            mysqlPass = str( a )

        if o in ( '--db', ):
            mysqlDb = str( a )

        if o in ( '--mythrec', ):
            mythtvRecPath = str( a )

    resourceMonitor = ResourceMonitor()
    connMythTv      = None

    try:
        connMythTv = MySQLdb.connect( host        = mysqlHost,
                                      user        = mysqlUser,
                                      passwd      = mysqlPass,
                                      db          = mysqlDb,
                                      use_unicode = True )
    except MySQLdb.Error, e:
        logger.error( "Unable to open MythTV database: error %d: %s" % ( e.args[0], e.args[1] ) )

    if connMythTv:
        mythTvChannels = MythTvChannel.getAllFromDb( connMythTv )
        for channel in mythTvChannels:
            logger.debug( "%s" % channel.dump() )

        mythTvIptvChannels = MythTvIptvChannel.getAllFromDb( connMythTv )
        for channel in mythTvIptvChannels:
            logger.debug( "%s" % channel.dump() )

        mythTvRecords = MythTvRecord.getAllFromDb( connMythTv )
        for record in mythTvRecords:
            logger.debug( "%s" % record.dump() )

        mythTvRecorded = MythTvRecorded.getAllFromDb( connMythTv )
        for recorded in mythTvRecorded:
            logger.debug( "%s" % recorded.dump() )

        mythTvOldRecorded = MythTvOldRecorded.getAllFromDb( connMythTv )
        for recorded in mythTvOldRecorded:
            logger.debug( "%s" % recorded.dump() )

        mythTvRecordedPrograms = MythTvRecordedProgram.getAllFromDb( connMythTv )
        for recordedProgram in mythTvRecordedPrograms:
            logger.debug( "%s" % recordedProgram.dump() )

        mythTvChannelsDict         = { x.chanId: x for x in mythTvChannels }
        mythTvIptvChannelsDict     = { x.chanId: x for x in mythTvIptvChannels }
        mythTvRecordedDict         = { "%i_%i" % ( x.chanId, x.programStart ): x for x in mythTvRecorded }
        mythTvOldRecordedDict      = { "%i_%i" % ( x.chanId, x.startTime ):    x for x in mythTvOldRecorded }
        mythTvRecordedProgramsDict = { "%i_%i" % ( x.chanId, x.startTime ):    x for x in mythTvRecordedPrograms }

        mythTvRecordMap         = {}
        mythTvChannelMap        = {}
        mythTvChannelUrlTypeMap = {}

        # TODO: storage path: storagegroup.groupname == 'Default'

        conn = DBConnection()

        if conn:
            try:
                # Create a channel map to map channels between MythTV and AminoPVR
                for mythTvChannel in mythTvChannels:
                    if mythTvChannel.chanId in mythTvIptvChannelsDict:
                        mythTvIptvChannel = mythTvIptvChannelsDict[mythTvChannel.chanId]
                    else:
                        logger.warning( "channel with chanId=%i not found in mythTvIptvChannelsDict" % ( mythTvChannel.chanId ) )

                    # The xmlTvId in MythTV is known as epgId in AminoPVR
                    # Search for AminoPVR channels with the same epgId
                    # Then match the Iptv Channel Url against AminoPVR ChannelUrl's
                    epgId             = mythTvChannel.xmlTvId
                    currChannels      = Channel.getAllByEpgIdFromDb( conn, epgId, includeInactive=True )
                    for channel in currChannels:
                        if mythTvIptvChannel:
                            for urlType in channel.urls.keys():
                                url     = channel.urls[urlType]
                                urlPart = "%s:%i" % ( url.ip, url.port )
                                if urlPart in mythTvIptvChannel.url:
                                    logger.warning( "Channel Match: chanId=%i, channel=%s, urlType=%s" % ( mythTvChannel.chanId, channel.dump(), urlType ) )
                                    mythTvChannelMap[mythTvChannel.chanId]        = channel
                                    mythTvChannelUrlTypeMap[mythTvChannel.chanId] = urlType
                                    break

                    # We didn't find a match
                    if mythTvChannel.chanId not in mythTvChannelMap:
                        if len( currChannels ) > 0:
                            logger.warning( "Channels found, but no Url match for chanId=%i, epgId=%s" % ( mythTvChannel.chanId, epgId ) )
                            mythTvChannelMap[mythTvChannel.chanId]        = currChannels[0]
                            mythTvChannelUrlTypeMap[mythTvChannel.chanId] = "sd"
                            for channel in currChannels:
                                logger.info( "Channel: %s" % ( channel.dump() ) )
                        else:
                            logger.warning( "No channels found for chanId=%i, epgId=%s" % ( mythTvChannel.chanId, epgId ) )

                # Convert MythTV records (schedule entries) to AminoPVR schedules
                for record in mythTvRecords:
                    # If the channel is not in the channel map (yet), it does not exist
                    # in the AminoPVR database.
                    # If there is enough information on MythTV side, create an inactive
                    # channel.
                    if record.chanId != 0 and record.chanId not in mythTvChannelMap:
                        channel, urlType =_addChannel( record.chanId, mythTvChannelsDict, mythTvIptvChannelsDict, dryRun )
                        if channel:
                            logger.warning( "Adding Channel: %s" % ( channel.dump() ) )
                            if not dryRun:
                                channel.addToDb( conn )
                            mythTvChannelMap[record.chanId]        = channel
                            mythTvChannelUrlTypeMap[record.chanId] = urlType

                    if record.chanId == 0 or record.chanId in mythTvChannelMap:
                        channelId = -1
                        if record.chanId:
                            channelId = mythTvChannelMap[record.chanId].id
 
                        recType   = Schedule.SCHEDULE_TYPE_ANY_TIME
                        dupMethod = Schedule.DUPLICATION_METHOD_NONE
                        if record.type == 1:    # kSingleRecord
                            recType = Schedule.SCHEDULE_TYPE_ONCE
                        elif record.type == 2:  # kTimeslotRecord
                            recType = Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_DAY
                        elif record.type == 3:  # kChannelRecord
                            recType = Schedule.SCHEDULE_TYPE_ANY_TIME
                            if channelId == -1:
                                logger.warning( "Expecting a channelId in record %s" % ( record.dump() ) )
                                if not dryRun:  # on the dry-run there might be new channels added, so they don't have a valid id yet.
                                    continue
                        elif record.type == 4:  # kAllRecord
                            recType   = Schedule.SCHEDULE_TYPE_ANY_TIME
                            channelId = -1
                        elif record.type == 5:  # kWeekslotRecord
                            recType = Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK
                        elif record.type == 9:  # kFindDailyRecord
                            recType = Schedule.SCHEDULE_TYPE_ONCE_EVERY_DAY
                        elif record.type == 10: # kFindWeeklyRecord
                            recType = Schedule.SCHEDULE_TYPE_ONCE_EVERY_WEEK

                        # Search for a Schedule with the same title and channelId
                        schedule = Schedule.getByTitleAndChannelIdFromDb( conn, record.title, channelId )

                        # No schedule exists yet, create one
                        if not schedule:
                            if record.dupMethod & 0x02 == 0x02: # kDupCheckSub
                                dupMethod = dupMethod | Schedule.DUPLICATION_METHOD_SUBTITLE
                            if record.dupMethod & 0x04 == 0x04: # kDupCheckDesc
                                dupMethod = dupMethod | Schedule.DUPLICATION_METHOD_DESCRIPTION
                            if record.dupMethod & 0x08 == 0x08: # kDupCheckSubThenDesc
                                dupMethod = dupMethod | Schedule.DUPLICATION_METHOD_SUBTITLE | Schedule.DUPLICATION_METHOD_DESCRIPTION

                            schedule                    = Schedule()
                            schedule.type               = recType
                            schedule.channelId          = channelId
                            schedule.startTime          = record.startTime
                            schedule.endTime            = record.endTime
                            schedule.title              = record.title
                            schedule.preferHd           = (channelId != -1 and mythTvChannelUrlTypeMap[record.chanId] != u"sd")
                            schedule.preferUnscrambled  = False
                            schedule.dupMethod          = dupMethod
                            schedule.startEarly         = round( record.startOffset / 60 )
                            schedule.endLate            = round( record.endOffset / 60 )
                            schedule.inactive           = record.inactive
 
                            logger.warning( "Adding Schedule: %s" % ( schedule.dump() ) )
 
                            if not dryRun:
                                schedule.addToDb( conn )
                        else:
                            logger.warning( "Schedule with title=%s and channelId=%i already exists" % ( schedule.title, schedule.channelId ) )
 
                        mythTvRecordMap[record.recordId] = schedule
 
                for recordKey in mythTvOldRecordedDict.keys():
                    recorded = mythTvOldRecordedDict[recordKey]

                    if recordKey not in mythTvRecordedDict:
                        # If the channel is not in the channel map (yet), it does not exist
                        # in the AminoPVR database.
                        # If there is enough information on MythTV side, create an inactive
                        # channel.
                        if recorded.chanId not in mythTvChannelMap:
                            channel, urlType =_addChannel( recorded.chanId, mythTvChannelsDict, mythTvIptvChannelsDict, dryRun )
                            if channel:
                                logger.warning( "Adding Channel: %s" % ( channel.dump() ) )
                                if not dryRun:
                                    channel.addToDb( conn )
                                mythTvChannelMap[recorded.chanId]        = channel
                                mythTvChannelUrlTypeMap[recorded.chanId] = urlType

                        if recorded.chanId in mythTvChannelMap:
                            channel = mythTvChannelMap[recorded.chanId]

                            scheduleId = -1
                            if recorded.recordId in mythTvRecordMap:
                                scheduleId = mythTvRecordMap[recorded.recordId].id
                            else:
                                logger.debug( "record with recordId=%i not found in mythTvRecordMap (%s)" % ( recorded.recordId, recorded.dump() ) )

                            recordingProgram = RecordingProgram.getByOriginalIdFromDb( conn, recordKey )
                            recording        = None

                            if not recordingProgram:
                                recordingProgram                = RecordingProgram()
                                recordingProgram.epgId          = channel.epgId
                                recordingProgram.originalId     = recordKey
                                recordingProgram.startTime      = recorded.startTime
                                recordingProgram.endTime        = recorded.endTime
                                recordingProgram.title          = recorded.title
                                recordingProgram.subtitle       = recorded.subtitle
                                recordingProgram.description    = recorded.description
                                recordingProgram.detailed       = True
                                if recorded.category in _CATTRANS:
                                    genre = Genre.getByGenreFromDb( conn, _CATTRANS[recorded.category] )
                                    if not genre:
                                        genre       = Genre()
                                        genre.genre = _CATTRANS[recorded.category]
                                    programGenre        = RecordingProgramGenre()
                                    programGenre.genre  = genre
                                    recordingProgram.genres = [ programGenre ]
                            else:
                                logger.warning( "Recording program with originalId=%s already exists" % ( recordKey ) )
                                recording = Recording.getByEpgProgramIdFromDb( conn, recordingProgram.id )
                                if not recording:
                                    recording = OldRecording.getByEpgProgramIdFromDb( conn, recordingProgram.id )

                            if not recording:
                                recording                   = OldRecording()
                                recording.scheduleId        = scheduleId
                                recording.epgProgramId      = recordingProgram.id
                                recording.channelId         = channel.id
                                recording.channelName       = channel.name
                                recording.channelUrlType    = mythTvChannelUrlTypeMap[recordedProgram.chanId]
                                recording.startTime         = recorded.startTime
                                recording.endTime           = recorded.endTime
                                recording.length            = recorded.endTime - recorded.startTime
                                recording.title             = recorded.title
                                recording.filename          = recordKey
                                recording.fileSize          = 0
                                recording.type              = mythTvChannelUrlTypeMap[recordedProgram.chanId]
                                recording.status            = RecordingState.RECORDING_FINISHED
                                recording.epgProgram        = recordingProgram
                                logger.warning( "Adding Old Recording: %s" % ( recording.dump() ) )
                                if not dryRun:
                                    recording.addToDb( conn )

                            # TODO: copy/move/link recording files & recording index
                            else:
                                logger.warning( "(Old) Recording with epgProgramId=%i already exists" % ( recordingProgram.id ) )
                        else:
                            logger.warning( "channel with chanId=%i not found in mythTvChannelMap (%s)" % ( recordedProgram.chanId, recordedProgram.dump() ) )
                    else:
                        logger.warning( "(Old) Recording with recordKey=%s is still in recording list" % ( recordKey ) )

                for recordKey in mythTvRecordedDict.keys():
                    if recordKey in mythTvRecordedProgramsDict:
                        recorded        = mythTvRecordedDict[recordKey]
                        recordedProgram = mythTvRecordedProgramsDict[recordKey]

                        # If the channel is not in the channel map (yet), it does not exist
                        # in the AminoPVR database.
                        # If there is enough information on MythTV side, create an inactive
                        # channel.
                        if recordedProgram.chanId not in mythTvChannelMap:
                            channel, urlType =_addChannel( recordedProgram.chanId, mythTvChannelsDict, mythTvIptvChannelsDict, dryRun )
                            if channel:
                                logger.warning( "Adding Channel: %s" % ( channel.dump() ) )
                                if not dryRun:
                                    channel.addToDb( conn )
                                mythTvChannelMap[record.chanId]        = channel
                                mythTvChannelUrlTypeMap[record.chanId] = urlType

                        if recordedProgram.chanId in mythTvChannelMap:
                            channel = mythTvChannelMap[recordedProgram.chanId]

                            scheduleId = -1
                            if recorded.recordId in mythTvRecordMap:
                                scheduleId = mythTvRecordMap[recorded.recordId].id
                            else:
                                logger.debug( "record with recordId=%i not found in mythTvRecordMap (%s)" % ( recorded.recordId, recorded.dump() ) )

                            recordingProgram = RecordingProgram.getByOriginalIdFromDb( conn, recordKey )
                            recording        = None

                            if not recordingProgram:
                                recordingProgram                = RecordingProgram()
                                recordingProgram.epgId          = channel.epgId
                                recordingProgram.originalId     = recordKey
                                recordingProgram.startTime      = recordedProgram.startTime
                                recordingProgram.endTime        = recordedProgram.endTime
                                recordingProgram.title          = recordedProgram.title
                                recordingProgram.subtitle       = recordedProgram.subtitle
                                recordingProgram.description    = recordedProgram.description
                                recordingProgram.detailed       = True
                                if recordedProgram.category in _CATTRANS:
                                    genre = Genre.getByGenreFromDb( conn, _CATTRANS[recordedProgram.category] )
                                    if not genre:
                                        genre       = Genre()
                                        genre.genre = _CATTRANS[recordedProgram.category]
                                    programGenre        = RecordingProgramGenre()
                                    programGenre.genre  = genre
                                    recordingProgram.genres = [ programGenre ]
                            else:
                                logger.warning( "Recording program with originalId=%s already exists" % ( recordKey ) )
                                recording = Recording.getByEpgProgramIdFromDb( conn, recordingProgram.id )
 
                            if not recording:
                                recording                   = Recording()
                                recording.scheduleId        = scheduleId
                                recording.epgProgramId      = recordingProgram.id
                                recording.channelId         = channel.id
                                recording.channelName       = channel.name
                                recording.channelUrlType    = mythTvChannelUrlTypeMap[recordedProgram.chanId]
                                recording.startTime         = recorded.startTime
                                recording.endTime           = recorded.endTime
                                recording.length            = recorded.endTime - recorded.startTime
                                recording.title             = recorded.title
                                recording.filename          = recorded.baseName
                                recording.fileSize          = recorded.fileSize
                                recording.type              = mythTvChannelUrlTypeMap[recordedProgram.chanId]
                                recording.status            = RecordingState.RECORDING_FINISHED
                                recording.epgProgram        = recordingProgram
                                logger.warning( "Adding Recording: %s" % ( recording.dump() ) )
                                if not dryRun:
                                    recording.addToDb( conn )

                                if not os.path.exists( os.path.abspath( os.path.join( generalConfig.recordingsPath, recording.filename ) ) ):
                                    logger.warning( "Linking \"%s\" to \"%s\"" % ( os.path.join( mythtvRecPath, recorded.baseName ), os.path.abspath( os.path.join( generalConfig.recordingsPath, recording.filename ) ) ) )
                                    if not dryRun:
                                        try:
                                            os.symlink( os.path.join( mythtvRecPath, recorded.baseName ), os.path.join( generalConfig.recordingsPath, recording.filename ) )
                                        except OSError, e:
                                            logger.error( "Unable to create symbolic link" )
                                            logger.error( traceback.format_exc() )
                            else:
                                logger.warning( "Recording with epgProgramId=%i already exists" % ( recordingProgram.id ) )
                        else:
                            logger.warning( "channel with chanId=%i not found in mythTvChannelMap (%s)" % ( recordedProgram.chanId, recordedProgram.dump() ) )
                    else:
                        logger.warning( "recordKey=%s not found in mythTvRecordedProgramsDict" % ( recordKey ) )
            except:
                logger.error( traceback.format_exc() )
        else:
            logger.error( "Unable to open AminoPVR database" )

    resourceMonitor.stop()

    sys.exit( 0 )

if __name__ == "__main__":
    main()
