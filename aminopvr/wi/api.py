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
from Queue import Queue, Empty
from aminopvr import schedule
from aminopvr.channel import PendingChannel, PendingChannelUrl, Channel, \
    ChannelUrl
from aminopvr.config import GeneralConfig, Config
from aminopvr.db import DBConnection
from aminopvr.epg import EpgProgram
from aminopvr.input_stream import InputStreamProtocol
from aminopvr.recording import Recording
from aminopvr.schedule import Schedule
from aminopvr.scheduler import Scheduler
from aminopvr.tools import Singleton, getFreeTotalSpaceMb
from cherrypy.lib.static import serve_file
import aminopvr.providers
import cherrypy
import json
import logging
import mimetypes
import os
import re
import socket
import struct
import threading
import types
import urllib

class Controller( object ):
    __metaclass__ = Singleton

    TYPE_CONTROLLER = 1
    TYPE_RENDERER   = 2

    def __init__( self ):
        self._listeners  = {}
        self._listenerId = 0
        self._lock       = threading.RLock()

    def addListener( self, ip, type ):
        listenerId = -1
        with self._lock:
            for id in self._listeners:
                if ip == self._listeners[id]["ip"] and type == self._listeners[id]["type"]:
                    listenerId = id
                    break
            if listenerId != -1:
                self.removeController( id )

            listener   = { "ip": ip, "type": type, "queue": Queue() }
            listenerId = self._listenerId
            self._listeners[listenerId] = listener
            self._listenerId += 1
        return listenerId

    def removeController( self, id ):
        with self._lock:
            if id in self._listeners:
                del self._listeners[id]

    def isListener( self, id ):
        with self._lock:
            if id in self._listeners:
                return True
        return False

    def getListeners( self ):
        listeners = []
        with self._lock:
            for id in self._listeners:
                listeners.append( { "id": id, "ip": self._listeners[id]["ip"], "type": self._listeners[id]["type"] } )
        return listeners

    def sendMessage( self, fromId, toIp, toType, message ):
        with self._lock:
            if fromId not in self._listeners:
                return False
        listener = self._getListener( toIp, toType )
        if listener:
            if "from" not in message:
                message["from"] = fromId
            listener["queue"].put( message )
            return True
        return False

    def getMessage( self, id, timeout=25.0 ):
        listener = None
        with self._lock:
            if id in self._listeners:
                listener = self._listeners[id]
        if listener:
            try:
                message = listener["queue"].get( True, timeout )
            except Empty:
                return None
            return message
        return None

    def _getListener( self, ip, type ):
        with self._lock:
            for id in self._listeners:
                if ip == self._listeners[id]["ip"] and type == self._listeners[id]["type"]:
                    return self._listeners[id]
        return None

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

            generalConfig = GeneralConfig( Config() )
            if apiKey:
                cls._apiKey = generalConfig.apiKey
                if apiKey == cls._apiKey:
                    access = True
                else:
                    cls._apiLogger.error( "_grantAccess: incorrect apiKey: clientIP=%s, apiKey=%s" % ( clientIP, apiKey ) )

            if not access:
                cls._apiLogger.debug( "_grantAccess: clientIP=%s" % ( clientIP ) )
                access = cls._addressInNetwork( clientIP, generalConfig.localAccessNets )

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
    def setChannelList( self, channelList ):
        self._logger.debug( "setChannelList( %s )" % ( channelList ) )

        try:
            channels = json.loads( channelList )
            conn     = DBConnection()

            newChannelNumbers = []

            for channel in channels:
                channelId  = -1
                channelOld = PendingChannel.getByNumberFromDb( conn, channel["id"] )
                if channelOld:
                    channelId = channelOld.id
                channelNew = self._getChannelFromJson( channel, channelId )
                newChannelNumbers.append( channelNew.number )
                self._logger.info( "setChannelList: processing channel: %s" % ( channelNew.dump() ) )
                if not channelNew:
                    self._logger.error( "setChannelList: unable to create channel for channel=%s", ( channel ) )
                elif not channelOld:
                    self._logger.info( "setChannelList: adding channel: %i - %s" % ( channelNew.number, channelNew.name ) )
                    channelNew.addToDb( conn )
                elif channelOld != channelNew:
                    self._logger.info( "setChannelList: updating channel: %i - %s" % ( channelNew.number, channelNew.name ) )
                    channelNew.addToDb( conn )

            currentChannels       = PendingChannel.getAllFromDb( conn, includeRadio=True, tv=True )
            currentChannelNumbers = [ channel.number for channel in currentChannels ]
            removedChannelNumbers = set( currentChannelNumbers ).difference( set( newChannelNumbers ) )

            for number in removedChannelNumbers:
                channel = PendingChannel.getByNumberFromDb( conn, number )
                if channel:
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
            logger = logging.getLogger( "aminopvr.STB.%s" % ( log["module"] ) )
            if log["level"] == 0:
                logger.debug( "%d %s" % ( log["timestamp"], urllib.unquote( log["log_text"] ) ) )
            elif log["level"] == 1:
                logger.info( "%d %s" % ( log["timestamp"], urllib.unquote( log["log_text"] ) ) )
            elif log["level"] == 2:
                logger.warning( "%d %s" % ( log["timestamp"], urllib.unquote( log["log_text"] ) ) )
            elif log["level"] == 3:
                logger.error( "%d %s" % ( log["timestamp"], urllib.unquote( log["log_text"] ) ) )
            elif log["level"] == 4:
                logger.critical( "%d %s" % ( log["timestamp"], urllib.unquote( log["log_text"] ) ) )
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

class ControllerAPI( API ):
    _logger = logging.getLogger( "aminopvr.WI.ControllerAPI" )

    @cherrypy.expose
    @API._grantAccess
    def init( self, type=0 ):
        self._logger.debug( "init( type=%s )" % ( type ) )
        type       = int( type )
        controller = Controller()
        id         = controller.addListener( cherrypy.request.remote.ip, type )
        self._logger.warning( "init: added listener with id=%d for ip=%s and type=%d" % ( id, cherrypy.request.remote.ip, type ) )
        # Send a message to the requester if it is a RENDERER to set the channel list
        if type == Controller.TYPE_RENDERER:
            if controller.sendMessage( id, cherrypy.request.remote.ip, type, { "type": "command", "data": { "command": "setChannelList" } } ):
                self._logger.warning( "init: send message to self request channel list" )
            else:
                self._logger.error( "init: failed to send message to self" )
            for header in cherrypy.request.headers:
                self._logger.info( "init: listener header: %s: %s" % ( header, cherrypy.request.headers[header] ) )
        return self._createResponse( API.STATUS_SUCCESS, { "id": id } )

    @cherrypy.expose
    @API._grantAccess
    def poll( self, id=-1 ):
        self._logger.debug( "poll( id=%s )" % ( id ) )
        id         = int( id )
        controller = Controller()
        if controller.isListener( id ):
            message = controller.getMessage( id, 25 )
            if message:
                self._logger.warning( "poll: message received: from=%d, type=%s" % ( message["from"], message["type"] ) )
                return self._createResponse( API.STATUS_SUCCESS, message )
            else:
                return self._createResponse( API.STATUS_SUCCESS, { "type": "timeout" } )
        else:
            self._logger.warning( "poll: listener with id=%d not registered" % ( id ) )
            return self._createResponse( API.STATUS_FAIL, { "message": "Listener with id=%d is not registered" % ( id ) } )

    @cherrypy.expose
    @API._grantAccess
    def sendMessage( self, fromId, toId, message ):
        self._logger.debug( "sendMessage( fromId=%s, toId=%s, message=%s )" %  fromId, toId, message )
        fromId = int( fromId )
        toId   = int( toId )
        controller = Controller()
        if not controller.isListener( fromId ):
            return self._createResponse( API.STATUS_FAIL, { "message": "Listener with id=%d is not registered" % ( fromId ) } )
        if not controller.isListener( toId ):
            return self._createResponse( API.STATUS_FAIL, { "message": "Listener with id=%d is not registered" % ( toId ) } )
        if controller.sendMessage( fromId, toId, message ):
            return self._createResponse( API.STATUS_SUCCESS, None )
        return self._createResponse( API.STATUS_FAIL, { "message": "Couldn't send message from %d to %d" % ( fromId, toId ) } )

    @cherrypy.expose
    @API._grantAccess
    def getListenerList( self ):
        controller = Controller()
        listeners  = controller.getListeners()
        return self._createResponse( API.STATUS_SUCCESS, listeners )

class AminoPVRAPI( API ):

    _logger = logging.getLogger( "aminopvr.WI.AminoPVRAPI" )

    stb        = STBAPI()
    controller = ControllerAPI()

    @cherrypy.expose
    @API._grantAccess
    def index( self ):
        return "Welcome to AminoPVR API"

    @cherrypy.expose
    @API._grantAccess
    def getNumChannels( self ):
        self._logger.debug( "getNumChannels()" )
        conn = DBConnection()
        return self._createResponse( API.STATUS_SUCCESS, { "num_channels": Channel.getNumChannelsFromDb( conn ) } )

    @cherrypy.expose
    @API._grantAccess
    def getChannelList( self, tv=True, radio=False, unicast=True, includeScrambled=False, includeHd=True ):
        self._logger.debug( "getChannelList( tv=%s, radio=%s, unicast=%s, includeScrambled=%s, includeHd=%s )" % ( tv, radio, unicast, includeScrambled, includeHd ) )
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
        self._logger.debug( "getEpgForChannel( channelId=%s, startTime=%s, endTime=%s )" % ( channelId, startTime, endTime ) )
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
    def getNowNextProgramList( self ):
        self._logger.debug( "getNowNextProgramList()" )
        conn     = DBConnection()
        epgData  = EpgProgram.getNowNextFromDb( conn )
        epgDict  = {}
        for epg in epgData:
            if epg.epgId not in epgDict:
                epgDict[epg.epgId] = []
            epgDict[epg.epgId].append( epg.toDict() )
        return self._createResponse( API.STATUS_SUCCESS, epgDict )

    @cherrypy.expose
    @API._grantAccess
    def getStorageInfo( self ):
        self._logger.debug( "getStorageInfo()" )
        generalConfig = GeneralConfig( Config() )
        free, total   = getFreeTotalSpaceMb( generalConfig.recordingsPath )
        return self._createResponse( API.STATUS_SUCCESS, { "available_size": free, "total_size": total } )

    @cherrypy.expose
    @API._grantAccess
    def getNumRecordings( self ):
        self._logger.debug( "getNumRecordings()" )
        conn = DBConnection()
        return self._createResponse( API.STATUS_SUCCESS, { "num_recordings": Recording.getNumRecordingsFromDb( conn ) } )

    @cherrypy.expose
    @API._grantAccess
    # TODO: this is still very STB oriented --> define proper API here and in JavaScript
    def getRecordingList( self, offset=None, count=None, sort=None ):
        self._logger.debug( "getRecordingList( offset=%s, count=%s, sort=%s )" % ( offset, count, sort ) )

        if offset:
            offset = int( offset )
        if count:
            count  = int( count )

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
    def deleteRecording( self, id, rerecord=False ):
        self._logger.debug( "deleteRecording( id=%s, rerecord=%s )" % ( id, rerecord ) )
        conn        = DBConnection()
        rerecord    = int( rerecord )
        recordingId = int( id )
        recording   = Recording.getFromDb( conn, recordingId )
        if recording:
            recording.deleteFromDb( conn, rerecord )
            return self._createResponse( API.STATUS_SUCCESS )
        else:
            self._logger.warning( "deleteRecording: recording with id=%d does not exist" % ( recordingId ) )

    @cherrypy.expose
    @API._grantAccess
    def getRecordingMeta( self, id ):
        self._logger.debug( "getRecordingMeta( id=%s )" % ( id ) )
        return self._createResponse( API.STATUS_SUCCESS, { "marker": 0 } )

    @cherrypy.expose
    @API._grantAccess
    def setRecordingMeta( self, id, marker ):
        self._logger.debug( "setRecordingMeta( id=%s, marker=%s )" % ( id, marker ) )
        conn      = DBConnection()
        recording = Recording.getFromDb( conn, int( id ) )
        if recording:
            recording.marker = int( marker )
            recording.addToDb( conn )
            return self._createResponse( API.STATUS_SUCCESS )
        return self._createResponse( API.STATUS_FAIL )

    @cherrypy.expose
    @API._grantAccess
    # TODO: this is still very STB oriented --> define proper API here and in JavaScript
    def getScheduleList( self ):
        self._logger.debug( "getScheduleList()" )
        conn           = DBConnection()
        schedules      = Schedule.getAllFromDb( conn, includeInactive=True )
        schedulesArray = []
        for schedule in schedules:
            scheduleJson = schedule.toDict()
            if scheduleJson:
                schedulesArray.append( scheduleJson )
        return self._createResponse( API.STATUS_SUCCESS, schedulesArray )

    @cherrypy.expose
    @API._grantAccess
    def getNumScheduledRecordings( self ):
        self._logger.debug( "getNumScheduledRecordings()" )
        scheduledRecordings = Scheduler().getScheduledRecordings()
        return self._createResponse( API.STATUS_SUCCESS, { "num_recordings": len( scheduledRecordings ) } )

    @cherrypy.expose
    @API._grantAccess
    # TODO: this is still very STB oriented --> define proper API here and in JavaScript
    def getScheduledRecordingList( self, offset=None, count=None, sort=None ):
        self._logger.debug( "getScheduledRecordingList( offset=%s, count=%s, sort=%s )" % ( offset, count, sort ) )
        if offset:
            offset = int( offset )
        if count:
            count  = int( count )
        scheduledRecordings = Scheduler().getScheduledRecordings()
        scheduledRecordingsArray = []
        for scheduledRecording in scheduledRecordings:
            scheduledRecordingJson = scheduledRecording.toDict()
            if scheduledRecordingJson:
                scheduledRecordingsArray.append( scheduledRecordingJson )
        return self._createResponse( API.STATUS_SUCCESS, scheduledRecordingsArray )

    @cherrypy.expose
    @API._grantAccess
    # TODO: this is still very STB oriented --> define proper API here and in JavaScript
    def addSchedule( self, url, titleId, startTime, endTime, aa ):
        self._logger.debug( "addSchedule( url=%s, titleId=%s, startTime=%d, endTime=%d, aa=%s )" % ( url, titleId, startTime, endTime, aa ) )
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
    def deleteSchedule( self, id ):
        self._logger.debug( "deleteSchedule( id=%s )" % ( id ) )
        return self._createResponse( API.STATUS_FAIL )

    @cherrypy.expose
    @API._grantAccess
    def changeSchedule( self, id ):
        self._logger.debug( "changeSchedule( id=%s )" % ( id ) )
        return self._createResponse( API.STATUS_FAIL )

    @cherrypy.expose
    @API._grantAccess
    def activatePendingChannels( self ):
        self._logger.debug( "activatePendingChannels()" )
        conn = DBConnection()
        pendingChannels = PendingChannel.getAllFromDb( conn, includeInactive=True, includeRadio=True, tv=True )

        pendingChannelNumbers = [ channel.number for channel in pendingChannels ]

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

                # Keep the scrambled setting from ChannelUrl's currently in the Db.
                # This setting cannot be retrieved from the source 
                for key in currChannel.urls.keys():
                    if newCurrChannel.urls.has_key( key ):
                        newCurrChannel.urls[key].scrambled = currChannel.urls[key].scrambled

                # Has the channel really changed?
                if newCurrChannel != currChannel:
                    self._logger.info( "activatePendingChannels: existing channel: %i - %s" % ( channel.number, channel.name ) )

                    # Hmm, channel number and name are the same, but epgId is different
                    if newCurrChannel.epgId != currChannel.epgId:
                        self._logger.info( "activatePendingChannels: epgId has changed: %s > %s" % ( currChannel.epgId, newCurrChannel.epgId ) )

                    # Make sure the changed channel is activated (again)
                    newCurrChannel.inactive = False

                    if currChannel.logo != "" and os.path.basename( newCurrChannel.logo ) != os.path.basename( currChannel.logo ):
                        currChannel.removeLogo( conn )
                    if currChannel.thumbnail != "" and os.path.basename( newCurrChannel.thumbnail ) != os.path.basename( currChannel.thumbnail ):
                        currChannel.removeThumbnail( conn )

                    # Download the logo and thumbnail for this channel
                    newCurrChannel.downloadLogoAndThumbnail()
                    newCurrChannel.addToDb( conn )
            else:
                self._logger.info( "activatePendingChannels: new channel: %i - %s" % ( channel.number, channel.name ) )
                newChannel = Channel.copy( channel )
                newChannel.downloadLogoAndThumbnail()
                newChannel.addToDb( conn )

        currentChannels       = Channel.getAllFromDb( conn, includeInactive=True, includeRadio=True, tv=True )
        currentChannelNumbers = [ channel.number for channel in currentChannels ]
        removedChannelNumbers = set( currentChannelNumbers ).difference( set( pendingChannelNumbers ) )

        self._logger.info( "activatePendingChannels: %i, %i, %i" % ( len( set( currentChannelNumbers ) ), len( set( pendingChannelNumbers ) ), len( removedChannelNumbers ) ) )
        for number in removedChannelNumbers:
            currChannel = Channel.getByNumberFromDb( conn, number )
            if not currChannel.inactive:
                self._logger.info( "activatePendingChannels: inactive channel: %i - %s" % ( currChannel.number, currChannel.name ) )
                currChannel.inactive = True
                currChannel.addToDb( conn )

        channels      = Channel.getAllFromDb( conn, includeRadio=True, tv=True )
        channelsArray = []

        for channel in channels:
            channelJson = channel.toDict( InputStreamProtocol.HTTP, includeScrambled=False, includeHd=True )
            if channelJson:
                channelsArray.append( channelJson )
        return self._createResponse( API.STATUS_SUCCESS, channelsArray )

    @cherrypy.expose
    @API._grantAccess
    def requestEpgUpdate( self ):
        self._logger.debug( "requestEpgUpdate()" )
        if aminopvr.providers.epgProvider:
            epgProvider = aminopvr.providers.epgProvider()
            if epgProvider.requestEpgUpdate():
                return self._createResponse( API.STATUS_SUCCESS )
            else:
                return self._createResponse( API.STATUS_FAIL )
        else:
            return self._createResponse( API.STATUS_FAIL )

class AminoPVRRecordings( API ):
    _logger = logging.getLogger( "aminopvr.WI.Recordings" )
    @cherrypy.expose
    @API._grantAccess
    def default( self, *args, **kwargs ):
        self._logger.debug( "default( %s, %s )" % ( str( args ), str( kwargs ) ) )

        for header in cherrypy.request.headers:
            self._logger.info( "default: header: %s: %s" % ( header, cherrypy.request.headers[header] ) )

        conn        = DBConnection()
        recordingId = list( args )[0]
        recording   = Recording.getFromDb( conn, recordingId )
        if recording:
            generalConfig = GeneralConfig( Config() )
            filename      = os.path.join( generalConfig.recordingsPath, recording.filename )
#            BUF_SIZE      = 16 * 1024

            if os.path.exists( filename ):
#                 f = open( filename, 'rb' )
#                 cherrypy.response.headers[ "Content-Type" ]   = mimetypes.guess_type( filename )[0]
#                 cherrypy.response.headers[ "Content-Length" ] = os.path.getsize( filename )
                return serve_file( os.path.abspath( filename ), content_type=mimetypes.guess_type( filename )[0] )
#                 def content():
#                     data = f.read( BUF_SIZE )
#                     while len( data ) > 0:
#                         yield data
#                         data = f.read( BUF_SIZE )
# 
#                 return content()
            else:
                return self._createResponse( API.STATUS_FAIL )
        else:
            return self._createResponse( API.STATUS_FAIL )
#    default._cp_config = { "response.stream": True } 

class AminoPVRWI( object ):

    _logger = logging.getLogger( "aminopvr.WI.AminoPVR" )

    api        = AminoPVRAPI()
    recordings = AminoPVRRecordings()

    @cherrypy.expose
    def index( self ):
        return "Welcome to AminoPVR"
