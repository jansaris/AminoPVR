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
from aminopvr.channel import PendingChannel, PendingChannelUrl
from aminopvr.db import DBConnection
from aminopvr.recorder import Recorder
import aminopvr
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
    def _grantAccess( self, apiKey=None ):
        if apiKey:
            # TODO: check against API key
            return True
        else:
            clientIP = cherrypy.request.remote.ip
            self._apiLogger.debug( "_grantAccess: clientIP=%s" % ( clientIP ) )
            return self._addressInNetwork( clientIP, aminopvr.generalConfig.localAccessNets )

    def _addressInNetwork( self, ip, nets ):
        # Is an address in a network
        ipAddress = struct.unpack( 'L', socket.inet_aton( ip ) )[0]
        self._apiLogger.debug( "_addressInNetwork( %s, %s )" % ( ip, nets ) )
        self._apiLogger.debug( "_addressInNetwork: type( nets )=%s )" % ( type( nets ) ) )
        if isinstance( nets, types.StringTypes ):
            if '/' in nets:
                netAddress, maskBits = nets.split( '/' )
                netmask = struct.unpack( 'L',socket.inet_aton( netAddress ) )[0] & ((2L << int( maskBits ) - 1) - 1)
                self._apiLogger.debug( "_addressInNetwork: ipAddress=%x, netmask=%x )" % ( ipAddress, netmask ) )
                return ipAddress & netmask == netmask
            else:
                netmask = struct.unpack( 'L',socket.inet_aton( nets ) )[0]
                self._apiLogger.debug( "_addressInNetwork: ipAddress=%x, netmask=%x )" % ( ipAddress, netmask ) )
                return ipAddress & netmask == netmask
        else:
            for net in nets:
                inNet = self._addressInNetwork( ip, net )
                if inNet:
                    return True
            return False
class STBAPI( API ):
    _logger = logging.getLogger( "aminopvr.WI.STBAPI" )

    @cherrypy.expose
    def poll( self, init=None ):
        self._logger.debug( "poll( %s )" % ( init ) )
        if self._grantAccess():
            if init == None:
                time.sleep( 25 )
                return json.dumps( { "type": "timeout" } )
            else:
                return json.dumps( { "type": "command", "command": "get_channel_list" } )
        else:
            self._logger.error( "poll: no access!" )
            return json.dumps( { "status": "no_access" } )

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

                return json.dumps( { "status": "success", "numChannels": len( channels ) } )
            except:
                self._logger.exception( "setChannelList: exception: channelList=%s" % ( channelList ) )

            return json.dumps( { "status": "fail", "numChannels": 0 } )
        else:
            self._logger.error( "setChannelList: no access!" )
            return json.dumps( { "status": "no_access" } )

    @cherrypy.expose
    def postLog( self, logData ):
        self._logger.debug( "postLog( %s )" % ( logData ) )
        if self._grantAccess():
            logs = json.loads( logData )
            for log in logs:
                self._logger.debug( "[%d] %d %s" % ( log["level"], log["timestamp"], urllib.unquote( log["log_text"] ) ) )
            return json.dumps( { "numLogs": len( logs ) } )
        else:
            self._logger.error( "postLog: no access!" )
            return json.dumps( { "status": "no_access" } )

    @cherrypy.expose
    def setActiveChannel( self, channel ):
        self._logger.debug( "setActiveChannel( %s )" % ( channel ) )
        if self._grantAccess():
            return json.dumps( { "status": "ok" } )
        else:
            self._logger.error( "setActiveChannel: no access!" )
            return json.dumps( { "status": "no_access" } )

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
    def getStorageInfo( self ):
        self._logger.debug( "getStorageInfo" )
        if self._grantAccess():
            # TODO: get actual storage info
            return json.dumps( { "available_size": 100000, "total_size": 200000 } )
        else:
            self._logger.error( "getStorageInfo: no access!" )
            return json.dumps( { "status": "no_access" } )

    @cherrypy.expose
    def getRecordingList( self ):
        self._logger.debug( "getRecordingList" )
        if self._grantAccess():
            return json.dumps( [] )
        else:
            self._logger.error( "getRecordingList: no access!" )
            return json.dumps( { "status": "no_access" } )

    @cherrypy.expose
    def getRecordingMeta( self, id ):
        self._logger.debug( "getRecordingMeta( %s )" )
        if self._grantAccess():
            return json.dumps( { "marker": 0 } )
        else:
            self._logger.error( "getRecordingMeta: no access!" )
            return json.dumps( { "status": "no_access" } )

    @cherrypy.expose
    def setRecordingMeta( self, id, marker ):
        self._logger.debug( "setRecordingMeta( %s, %s )" % ( id, marker ) )
        if self._grantAccess():
            return json.dumps( { "status": "ok" } )
        else:
            self._logger.error( "setRecordingMeta: no access!" )
            return json.dumps( { "status": "no_access" } )

    @cherrypy.expose
    def getScheduleList( self ):
        self._logger.debug( "getScheduleList" )
        if self._grantAccess():
            return json.dumps( [] )
        else:
            self._logger.error( "getScheduleList: no access!" )
            return json.dumps( { "status": "no_access" } )

    @cherrypy.expose
    def addSchedule( self, schedule ):
        self._logger.debug( "addSchedule( %s )" % ( schedule ) )
        if self._grantAccess():
            return json.dumps( { "status": "ok" } )
        else:
            self._logger.error( "addSchedule: no access!" )
            return json.dumps( { "status": "no_access" } )

    @cherrypy.expose
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

class AminoPVRWI( object ):

    _logger = logging.getLogger( "aminopvr.WI.AminoPVR" )

    api = AminoPVRAPI()

    @cherrypy.expose
    def index( self ):
        return "Welcome to AminoPVR"
