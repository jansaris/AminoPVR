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
from aminopvr.channel import PendingChannel, PendingChannelUrl, Channel
from aminopvr.db import DBConnection
from aminopvr.epg import EpgProgram
from aminopvr.input_stream import InputStreamProtocol
from aminopvr.recorder import Recorder
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

    _apiLogger = logging.getLogger( "aminopvr.WI.API" )

    STATUS_FAIL      = 1
    STATUS_SUCCESS   = 2

    def _grantAccess( self, apiKey=None ):
        access   = False
        clientIP = cherrypy.request.remote.ip
        if apiKey:
            self.apiKey = aminopvr.generalConfig.apiKey
            if apiKey == self.apiKey:
                access = True
            else:
                self._apiLogger.error( "_grandAccess: incorrect apiKey: clientIP=%s, apiKey=%s" % ( clientIP, apiKey ) )
        else:
            self._apiLogger.debug( "_grantAccess: clientIP=%s" % ( clientIP ) )
            access = self._addressInNetwork( clientIP, aminopvr.generalConfig.localAccessNets )

        if not access:
            raise cherrypy.HTTPError( 401 )
        return access

    def _addressInNetwork( self, ip, nets ):
        # Is an address in a network
        ipAddress = struct.unpack( '=L', socket.inet_aton( ip ) )[0]
        self._apiLogger.debug( "_addressInNetwork( %s, %s )" % ( ip, nets ) )
        self._apiLogger.debug( "_addressInNetwork: type( nets )=%s )" % ( type( nets ) ) )
        if isinstance( nets, types.StringTypes ):
            if '/' in nets:
                netAddress, maskBits = nets.split( '/' )
                netmask = struct.unpack( '=L', socket.inet_aton( netAddress ) )[0] & ((2L << int( maskBits ) - 1) - 1)
                self._apiLogger.debug( "_addressInNetwork: ipAddress=%x, netmask=%x )" % ( ipAddress, netmask ) )
                return ipAddress & netmask == netmask
            else:
                netmask = struct.unpack( '=L', socket.inet_aton( nets ) )[0]
                self._apiLogger.debug( "_addressInNetwork: ipAddress=%x, netmask=%x )" % ( ipAddress, netmask ) )
                return ipAddress & netmask == netmask
        else:
            for net in nets:
                inNet = self._addressInNetwork( ip, net )
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
    def poll( self, init=None ):
        self._logger.debug( "poll( %s )" % ( init ) )
        if self._grantAccess():
            if init == None:
                time.sleep( 25 )
                return self._createResponse( API.STATUS_SUCCESS, { "type": "timeout" } )
            else:
                return self._createResponse( API.STATUS_SUCCESS, { "type": "command", "command": "get_channel_list" } )
        else:
            self._logger.error( "poll: no access!" )
            return self._createResponse( API.STATUS_NO_ACCESS )

    @cherrypy.expose
    def setChannelList( self, channelList ):
        self._logger.debug( "setChannelList( %s )" % ( channelList ) )

        if self._grantAccess():
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
                    if not channelNew:
                        self._logger.error( "setChannelList: unable to create channel for channel=%s", ( channel ) )
                    elif not channelOld:
                        self._logger.info( "setChannelList: adding channel: %i - %s" % ( channelNew.number, channelNew.name ) )
                        channelNew.addToDb( conn )
                    elif channelOld != channelNew:
                        self._logger.info( "setChannelList: updating channel: %i - %s" % ( channelNew.number, channelNew.name ) )
                        channelNew.addToDb( conn )

                currentChannels = PendingChannel.getAllFromDb( conn )

                removedChannels = set( currentChannels ).difference( set( newChannels ) )
                for channel in removedChannels:
                    self._logger.info( "setChannelList: remove channel: %i - %s" % ( channel.number, channel.name ) )
                    channel.deleteFromDb( conn )

                return self._createResponse( API.STATUS_SUCCESS, { "numChannels": len( channels ) } )
            except:
                self._logger.exception( "setChannelList: exception: channelList=%s" % ( channelList ) )

            return self._createResponse( API.STATUS_FAIL, { "numChannels": 0 } )

    @cherrypy.expose
    def postLog( self, logData ):
        self._logger.debug( "postLog( %s )" % ( logData ) )
        if self._grantAccess():
            logs = json.loads( logData )
            for log in logs:
                self._logger.debug( "[%d] %d %s" % ( log["level"], log["timestamp"], urllib.unquote( log["log_text"] ) ) )
            return self._createResponse( API.STATUS_SUCCESS, { "numLogs": len( logs ) } )

    @cherrypy.expose
    def setActiveChannel( self, channel ):
        self._logger.debug( "setActiveChannel( %s )" % ( channel ) )
        if self._grantAccess():
            return self._createResponse( API.STATUS_SUCCESS )

    def _getChannelFromJson( self, json, channelId=-1 ):
        channel = PendingChannel( channelId, json["id"], json["epg_id"], json["name"], json["name_short"], json["logo"], json["thumbnail"], json["radio"], False )
#        if not orgChannel:
#            channel = Channel( -1, json["id"], json["epg_id"], json["name"], json["name_short"], json["logo"], json["thumbnail"], json["radio"] )
#        else:
#            channel.number    = json["id"]
#            channel.epgId     = json["epg_id"]
#            channel.name      = json["name"]
#            channel.nameShort = json["name_short"]
#            channel.logo      = json["logo"]
#            channel.thumbnail = json["thumbnail"]

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
    def index( self ):
        return "Welcome to AminoPVR API"

    @cherrypy.expose
    def getNumChannels( self, apiKey=None ):
        self._logger.debug( "getNumChannels" )
        if self._grantAccess( apiKey ):
            conn = DBConnection()
            return self._createResponse( API.STATUS_SUCCESS, { "num_channels": Channel.getNumChannelsFromDb( conn ) } )

    @cherrypy.expose
    def getChannels( self, tv=True, radio=False, unicast=True, includeScrambled=False, includeHd=True, apiKey=None ):
        self._logger.debug( "getChannels" )
        if self._grantAccess( apiKey ):
            conn          = DBConnection()
            channels      = Channel.getAllFromDb( conn, includeRadio=radio, tv=not radio )
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
    def getEpgForChannel( self, channelId, startTime=None, endTime=None, apiKey=None ):
        self._logger.debug( "getEpgForChannel" )
        if self._grantAccess( apiKey ):
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
    def getStorageInfo( self, apiKey=None ):
        self._logger.debug( "getStorageInfo" )
        if self._grantAccess( apiKey ):
            # TODO: get actual storage info
            return self._createResponse( API.STATUS_SUCCESS, { "available_size": 100000, "total_size": 200000 } )

    @cherrypy.expose
    def getRecordingList( self, apiKey=None ):
        self._logger.debug( "getRecordingList" )
        if self._grantAccess( apiKey ):
            return self._createResponse( API.STATUS_SUCCESS, [] )

    @cherrypy.expose
    def getRecordingMeta( self, id, apiKey=None ):
        self._logger.debug( "getRecordingMeta( %s )" )
        if self._grantAccess( apiKey ):
            return self._createResponse( API.STATUS_SUCCESS, { "marker": 0 } )

    @cherrypy.expose
    def setRecordingMeta( self, id, marker, apiKey=None ):
        self._logger.debug( "setRecordingMeta( %s, %s )" % ( id, marker ) )
        if self._grantAccess( apiKey ):
            return self._createResponse( API.STATUS_SUCCESS )

    @cherrypy.expose
    def getScheduleList( self, apiKey=None ):
        self._logger.debug( "getScheduleList" )
        if self._grantAccess( apiKey ):
            return self._createResponse( API.STATUS_SUCCESS, [] )

    @cherrypy.expose
    def addSchedule( self, schedule, apiKey=None ):
        self._logger.debug( "addSchedule( %s )" % ( schedule ) )
        if self._grantAccess( apiKey ):
            return self._createResponse( API.STATUS_SUCCESS )

    @cherrypy.expose
    def getActiveRecordings( self, apiKey=None ):
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
    def activatePendingChannels( self, apiKey=None ):
        self._logger.debug( "activatePendingChannels" )
        if self._grantAccess( apiKey ):
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

            return self.getChannels( radio=False, unicast=True, includeScrambled=False, includeHd=True, apiKey=apiKey )

    @cherrypy.expose
    def requestEpgUpdate( self, apiKey=None ):
        self._logger.debug( "requestEpgUpdate" )
        if self._grantAccess( apiKey ):
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
