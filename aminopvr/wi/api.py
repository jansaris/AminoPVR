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
from aminopvr import schedule
from aminopvr.channel import PendingChannel, PendingChannelUrl, Channel, \
    ChannelUrl
from aminopvr.db import DBConnection
from aminopvr.epg import EpgProgram
from aminopvr.input_stream import InputStreamProtocol
from aminopvr.recorder import Recorder
from aminopvr.recording import Recording
from aminopvr.schedule import Schedule
from aminopvr.scheduler import Scheduler
import aminopvr.providers
import cherrypy
import json
import logging
import re
import socket
import struct
import time
import types
import urllib

class API( object ):

    _apiLogger       = logging.getLogger( "aminopvr.WI.API" )

    STATUS_FAIL      = 1
    STATUS_SUCCESS   = 2

    @classmethod
    def _grantAccess( cls, target ):
        def wrapper( *args, **kwargs ):
            access   = False
            clientIP = cherrypy.request.remote.ip
            apiKey   = None

            if kwargs.has_key( "apiKey" ):
                apiKey = kwargs["apiKey"]
                del kwargs["apiKey"]

            if apiKey:
                cls._apiKey = aminopvr.generalConfig.apiKey
                if apiKey == cls._apiKey:
                    access = True
                else:
                    cls._apiLogger.error( "_grantAccess: incorrect apiKey: clientIP=%s, apiKey=%s" % ( clientIP, apiKey ) )

            if not access:
                cls._apiLogger.debug( "_grantAccess: clientIP=%s" % ( clientIP ) )
                access = cls._addressInNetwork( clientIP, aminopvr.generalConfig.localAccessNets )

            if not access:
                raise cherrypy.HTTPError( 401 )

            return target( *args, **kwargs )
        return wrapper

    @classmethod
    def _addressInNetwork( cls, ip, nets ):
        # Is an address in a network
        ipAddress = struct.unpack( '=L', socket.inet_aton( ip ) )[0]
        cls._apiLogger.debug( "_addressInNetwork( %s, %s )" % ( ip, nets ) )
        cls._apiLogger.debug( "_addressInNetwork: type( nets )=%s )" % ( type( nets ) ) )
        if isinstance( nets, types.StringTypes ):
            if '/' in nets:
                netAddress, maskBits = nets.split( '/' )
                netmask = struct.unpack( '=L', socket.inet_aton( netAddress ) )[0] & ((2L << int( maskBits ) - 1) - 1)
                cls._apiLogger.debug( "_addressInNetwork: ipAddress=%x, netmask=%x )" % ( ipAddress, netmask ) )
                return ipAddress & netmask == netmask
            else:
                netmask = struct.unpack( '=L', socket.inet_aton( nets ) )[0]
                cls._apiLogger.debug( "_addressInNetwork: ipAddress=%x, netmask=%x )" % ( ipAddress, netmask ) )
                return ipAddress & netmask == netmask
        else:
            for net in nets:
                inNet = cls._addressInNetwork( ip, net )
                if inNet:
                    return True
            return False

    def _createResponse( self, status, data=None ):
        response = {}
        response["status"] = "unknown"
        if status == API.STATUS_SUCCESS:
            response["status"] = "success"
        elif status == API.STATUS_FAIL:
            response["status"] = "fail"
        if data:
            response["data"] = data
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps( response )

class STBAPI( API ):
    _logger = logging.getLogger( "aminopvr.WI.STBAPI" )

    @cherrypy.expose
    @API._grantAccess
    def poll( self, init=None ):
        self._logger.debug( "poll( %s )" % ( init ) )
        if init == None:
            time.sleep( 25 )
            return self._createResponse( API.STATUS_SUCCESS, { "type": "timeout" } )
        else:
            return self._createResponse( API.STATUS_SUCCESS, { "type": "command", "command": "get_channel_list" } )

    @cherrypy.expose
    @API._grantAccess
    def setChannelList( self, channelList ):
        self._logger.debug( "setChannelList( %s )" % ( channelList ) )

        try:
            channels = json.loads( channelList )

            conn = DBConnection()

            newChannels = []

            for channel in channels:
                channelId  = -1
                channelOld = PendingChannel.getByNumberFromDb( conn, channel["id"] )
                if channelOld:
                    channelId = channelOld.id
                channelNew = self._getChannelFromJson( channel, channelId )
                newChannels.append( channelNew )
                self._logger.info( "setChannelList: processing channel: %s" % ( channelNew.dump() ) )
                if not channelNew:
                    self._logger.error( "setChannelList: unable to create channel for channel=%s", ( channel ) )
                elif not channelOld:
                    self._logger.info( "setChannelList: adding channel: %i - %s" % ( channelNew.number, channelNew.name ) )
                    channelNew.addToDb( conn )
                elif channelOld != channelNew:
                    self._logger.info( "setChannelList: updating channel: %i - %s" % ( channelNew.number, channelNew.name ) )
                    channelNew.addToDb( conn )

            currentChannels = PendingChannel.getAllFromDb( conn, includeRadio=True, tv=True )

            removedChannels = set( currentChannels ).difference( set( newChannels ) )
            for channel in removedChannels:
                self._logger.info( "setChannelList: remove channel: %i - %s" % ( channel.number, channel.name ) )
                channel.deleteFromDb( conn )

            return self._createResponse( API.STATUS_SUCCESS, { "numChannels": len( channels ) } )
        except:
            self._logger.exception( "setChannelList: exception: channelList=%s" % ( channelList ) )

        return self._createResponse( API.STATUS_FAIL, { "numChannels": 0 } )

    @cherrypy.expose
    @API._grantAccess
    def postLog( self, logData ):
        self._logger.debug( "postLog( %s )" % ( logData ) )
        logs = json.loads( logData )
        for log in logs:
            if log["level"] == 0:
                self._logger.debug( "STB: %d %s" % ( log["timestamp"], urllib.unquote( log["log_text"] ) ) )
            elif log["level"] == 1:
                self._logger.info( "STB: %d %s" % ( log["timestamp"], urllib.unquote( log["log_text"] ) ) )
            elif log["level"] == 2:
                self._logger.warning( "STB: %d %s" % ( log["timestamp"], urllib.unquote( log["log_text"] ) ) )
            elif log["level"] == 3:
                self._logger.error( "STB: %d %s" % ( log["timestamp"], urllib.unquote( log["log_text"] ) ) )
            elif log["level"] == 4:
                self._logger.critical( "STB: %d %s" % ( log["timestamp"], urllib.unquote( log["log_text"] ) ) )
        return self._createResponse( API.STATUS_SUCCESS, { "numLogs": len( logs ) } )

    @cherrypy.expose
    @API._grantAccess
    def setActiveChannel( self, channel ):
        self._logger.debug( "setActiveChannel( %s )" % ( channel ) )
        return self._createResponse( API.STATUS_SUCCESS )


    def _getChannelFromJson( self, json, channelId=-1 ):
        channel = PendingChannel( channelId, json["id"], json["epg_id"], json["name"], json["name_short"], json["logo"], json["thumbnail"], json["radio"], False )
        urlRe   = re.compile( r"(?P<protocol>[a-z]{3,5}):\/\/(?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}):(?P<port>[0-9]{1,5})(?P<arguments>;.*)?" )
        for stream in json["streams"]:
            urlMatch = urlRe.search( stream["url"] )
            if urlMatch:
                urlType   = u"sd"
                protocol  = urlMatch.group( "protocol" )
                ip        = urlMatch.group( "ip" )
                port      = int( urlMatch.group( "port" ) )
                arguments = u""
                if urlMatch.group( "arguments" ):
                    arguments = urlMatch.group( "arguments" )
                if stream["is_hd"]:
                    urlType = u"hd"
                channel.addUrl( PendingChannelUrl( urlType, protocol, ip, port, arguments ) )
        return channel


class AminoPVRAPI( API ):

    _logger = logging.getLogger( "aminopvr.WI.AminoPVRAPI" )

    stb = STBAPI()

    @cherrypy.expose
    @API._grantAccess
    def index( self ):
        return "Welcome to AminoPVR API"

    @cherrypy.expose
    @API._grantAccess
    def getNumChannels( self ):
        self._logger.debug( "getNumChannels" )
        conn = DBConnection()
        return self._createResponse( API.STATUS_SUCCESS, { "num_channels": Channel.getNumChannelsFromDb( conn ) } )

    @cherrypy.expose
    @API._grantAccess
    def getChannels( self, tv=True, radio=False, unicast=True, includeScrambled=False, includeHd=True ):
        self._logger.debug( "getChannels" )
        conn          = DBConnection()
        channels      = Channel.getAllFromDb( conn, includeRadio=radio, tv=tv )
        channelsArray = []

        protocol = InputStreamProtocol.HTTP
        if not unicast:
            protocol = InputStreamProtocol.MULTICAST

        for channel in channels:
            channelJson = channel.toDict( protocol, includeScrambled, includeHd )
            if channelJson:
                channelsArray.append( channelJson )
        return self._createResponse( API.STATUS_SUCCESS, channelsArray )

    @cherrypy.expose
    @API._grantAccess
    def getEpgForChannel( self, channelId, startTime=None, endTime=None ):
        self._logger.debug( "getEpgForChannel" )
        if startTime:
            startTime = int( startTime )
        if endTime:
            endTime   = int( endTime )

        conn     = DBConnection()
        channel  = Channel.getFromDb( conn, channelId )
        epgData  = EpgProgram.getAllByEpgIdFromDb( conn, channel.epgId, startTime, endTime )
        epgArray = []
        for epg in epgData:
            epgArray.append( epg.toDict() )
        return self._createResponse( API.STATUS_SUCCESS, epgArray )

    @cherrypy.expose
    @API._grantAccess
    def getStorageInfo( self ):
        self._logger.debug( "getStorageInfo" )
        # TODO: get actual storage info
        return self._createResponse( API.STATUS_SUCCESS, { "available_size": 100000, "total_size": 200000 } )

    @cherrypy.expose
    @API._grantAccess
    # TODO: this is still very STB oriented --> define proper API here and in JavaScript
    def getRecordingList( self, offset=None, count=None, sort=None ):
        self._logger.debug( "getRecordingList()" )
        conn            = DBConnection()
        recordings      = Recording.getAllFromDb( conn, offset=offset, count=count, sort=sort )
        recordingsArray = []
        for recording in recordings:
            recordingJson = recording.toDict()
            if recordingJson:
                recordingsArray.append( recordingJson )
        return self._createResponse( API.STATUS_SUCCESS, recordingsArray )

    @cherrypy.expose
    @API._grantAccess
    # TODO: this is still very STB oriented --> define proper API here and in JavaScript
    def getScheduleList( self ):
        self._logger.debug( "getScheduleList()" )
        return self._createResponse( API.STATUS_SUCCESS, [] )

    @cherrypy.expose
    @API._grantAccess
    # TODO: this is still very STB oriented --> define proper API here and in JavaScript
    def addSchedule( self, url, titleId, startTime, endTime, aa ):
        self._logger.debug( "addSchedule( %s, %s, %d, %d, %s )" % ( url, titleId, startTime, endTime, aa ) )
        conn      = DBConnection()

        # Split title and programId
        title, programId = titleId.split( "||[", 2 )

        # Find the program we would like to record
        program   = EpgProgram.getByOriginalIdFromDb( conn, programId )
        if program:
            urlRe = re.compile( r"(?P<protocol>[a-z]{3,5}):\/\/(?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}):(?P<port>[0-9]{1,5})(?P<arguments>;.*)?" )
            urlMatch = urlRe.search( url )

            # Decode url into ip and port
            if urlMatch:
                ip   = urlMatch.group( "ip" )
                port = int( urlMatch.group( "port" ) )

                # Find channelId which uses this ip/port combination
                channelId = ChannelUrl.getChannelByIpPortFromDb( conn, ip, port )
                if channelId:
                    # Get the associated channel
                    channel = Channel.getFromDb( conn, channelId )
                    if channel:
                        # See if we already have a schedule to record this program
                        schedule = Schedule.getByTitleAndChannelIdFromDb( conn, title, channel.id )
                        if schedule:
                            timeDiff = startTime - schedule.startTime
                            if schedule.type != Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_DAY and \
                               schedule.type != Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK:
                                # If the time diff is a week, then we seem to want to record once every week 
                                if timeDiff >= (7 * 24 * 60 * 60):
                                    schedule.type = Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK
                                # If the time diff is a week, then we seem to want to record once every day 
                                elif timeDiff >= (1 * 24 * 60 * 60):
                                    schedule.type = Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_DAY
                                schedule.addToDb( conn )
                                Scheduler.requestReschedule()
                        else:
                            schedule = Schedule( -1,
                                                 Schedule.SCHEDULE_TYPE_ONCE,
                                                 channelId,
                                                 startTime,
                                                 endTime,
                                                 title,
                                                 True,      # TODO
                                                 False,     # TODO
                                                 Schedule.DUPLICATION_METHOD_TITLE | Schedule.DUPLICATION_METHOD_SUBTITLE,
                                                 0,
                                                 0 )
                            schedule.addToDb( conn )
                            Scheduler.requestReschedule()

                        return self._createResponse( API.STATUS_SUCCESS, schedule.id )
                    else:
                        self._logger.warning( "addSchedule: Unable to find channel with channelId=%d" % ( channelId ) )
                else:
                    self._logger.warning( "addSchedule: Unable to find channel from ip=%s, port=%d" % ( ip, port ) )
            else:
                self._logger.warning( "addSchedule: Unable to match url=%s" % ( url ) )
        else:
            self._logger.warning( "addSchedule: Unable to find recording with originalId=%s" % ( programId ) )

        return self._createResponse( API.STATUS_FAIL, "Unknown" )

    @cherrypy.expose
    @API._grantAccess
    def getRecordingMeta( self, id ):
        self._logger.debug( "getRecordingMeta( %s )" )
        return self._createResponse( API.STATUS_SUCCESS, { "marker": 0 } )

    @cherrypy.expose
    @API._grantAccess
    def setRecordingMeta( self, id, marker ):
        self._logger.debug( "setRecordingMeta( %s, %s )" % ( id, marker ) )
        return self._createResponse( API.STATUS_SUCCESS )

    @cherrypy.expose
    @API._grantAccess
    def getActiveRecordings( self ):
        self._logger.debug( "getActiveRecordings" )
        activeRecordings = Recorder.getActiveRecordings()
        return r'''
<html>
    <head>
        <title>%s</title>
    </head>
    <body>
        <br/>
        Currently, there are %d recordings active
    </body>
</html>
''' % ( 'Active Recordings', len( activeRecordings ) )

    @cherrypy.expose
    @API._grantAccess
    def activatePendingChannels( self ):
        self._logger.debug( "activatePendingChannels" )
        conn = DBConnection()
        pendingChannels = PendingChannel.getAllFromDb( conn, includeInactive=True, includeRadio=True, tv=True )

        for channel in pendingChannels:
            currChannel = Channel.getByNumberFromDb( conn, channel.number )
            if currChannel and currChannel.epgId != channel.epgId:
                # Found a channel on the same channel number, but epgId is different
                # Find another match.
                self._logger.info( "activatePendingChannels: epgId mismatch for channel %i - %s: %s != %s" % ( channel.number, channel.name, channel.epgId, currChannel.epgId ) )
                # If channel name is the same (or partially the same), then they must have changed epgId
                # Else, try to find a channel that would match
                if (channel.name != currChannel.name)         and \
                   (not channel.name     in currChannel.name) and \
                   (not currChannel.name in channel.name):
                    currChannel   = None
                    epgIdChannels = Channel.getAllByEpgIdFromDb( conn, channel.epgId, includeInactive=True, includeRadio=True )
                    for epgIdChannel in epgIdChannels:
                        if (epgIdChannel.name == channel.name)      or \
                           (channel.name      in epgIdChannel.name) or \
                           (epgIdChannel.name in channel.name):
                            currChannel = epgIdChannel
                            break
                # TODO: if still no match is found (based on epgId), then look for similar names
                # and maybe equal urls 

            if currChannel:
                # Convert PendingChannel to Channel but keep channel id
                newCurrChannel = Channel.copy( channel, currChannel.id )
                # Has the channel really changed?
                if newCurrChannel != currChannel:
                    self._logger.info( "activatePendingChannels: existing channel: %i - %s" % ( channel.number, channel.name ) )
#                        self._logger.info( "%s == %s" % ( newCurrChannel.dump(), currChannel.dump() ) )

                    # Hmm, channel number and name are the same, but epgId is different
                    if newCurrChannel.epgId != currChannel.epgId:
                        self._logger.info( "activatePendingChannels: epgId has changed: %s > %s" % ( currChannel.epgId, newCurrChannel.epgId ) )

                    # Make sure the changed channel is activated (again)
                    newCurrChannel.inactive = False

                    # Keep the scrambled setting from ChannelUrl's currently in the Db.
                    # This setting cannot be retrieved from the source 
                    for key in currChannel.urls.keys():
                        if newCurrChannel.urls.has_key( key ):
                            newCurrChannel.urls[key].scrambled = currChannel.urls[key].scrambled

                    # TODO: delete logo and/or thumbnail if changed
                    #if os.path.basename( newCurrChannel.logo ) != os.path.basename( currChannel.logo ):
                    #    currChannel.removeLogo()
                    #if os.path.basename( newCurrChannel.thumbnail ) != os.path.basename( currChannel.thumbnail ):
                    #    currChannel.removeThumbnail()

                    # Download the logo and thumbnail for this channel
                    newCurrChannel.downloadLogoAndThumbnail()
                    newCurrChannel.addToDb( conn )
            else:
                self._logger.info( "activatePendingChannels: new channel: %i - %s" % ( channel.number, channel.name ) )
                newChannel = Channel.copy( channel )
                newChannel.downloadLogoAndThumbnail()
                newChannel.addToDb( conn )

        currentChannels = Channel.getAllFromDb( conn, includeInactive=True, includeRadio=True, tv=True )
        removedChannels = set( currentChannels ).difference( set( pendingChannels ) )

        self._logger.info( "activatePendingChannels: %i, %i, %i" % ( len( set( currentChannels ) ), len( set( pendingChannels ) ), len( removedChannels ) ) )
        for channel in removedChannels:
            currChannel = Channel.getByNumberFromDb( conn, channel.number )
            if not currChannel.inactive:
                self._logger.info( "activatePendingChannels: inactive channel: %i - %s" % ( channel.number, channel.name ) )
                currChannel.inactive = True
                currChannel.addToDb( conn )

        channels      = Channel.getAllFromDb( conn, includeRadio=True, tv=True )
        channelsArray = []

        for channel in channels:
            channelJson = channel.toDict( InputStreamProtocol.HTTP, includeScrambled=False, includeHd=True )
            if channelJson:
                channelsArray.append( channelJson )
        return self._createResponse( API.STATUS_SUCCESS, channelsArray )
#        return self.getChannels( tv=True, radio=True, unicast=True, includeScrambled=True, includeHd=True )

    @cherrypy.expose
    @API._grantAccess
    def requestEpgUpdate( self ):
        self._logger.debug( "requestEpgUpdate" )
        if aminopvr.providers.epgProvider:
            epgProvider = aminopvr.providers.epgProvider()
            if epgProvider.requestEpgUpdate():
                return self._createResponse( API.STATUS_SUCCESS )
            else:
                return self._createResponse( API.STATUS_FAIL )
        else:
            return self._createResponse( API.STATUS_FAIL )

class AminoPVRWI( object ):

    _logger = logging.getLogger( "aminopvr.WI.AminoPVR" )

    api = AminoPVRAPI()

    @cherrypy.expose
    def index( self ):
        return "Welcome to AminoPVR"
