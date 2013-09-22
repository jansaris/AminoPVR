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
from aminopvr.config import GeneralConfig, Config
from aminopvr.db import DBConnection
from aminopvr.input_stream import InputStreamProtocol
from aminopvr.tools import getFreeTotalSpaceMb
from aminopvr.wi.api.channels import ChannelsAPI
from aminopvr.wi.api.common import API
from aminopvr.wi.api.config import ConfigAPI
from aminopvr.wi.api.controller import ControllerAPI
from aminopvr.wi.api.epg import EpgAPI
from aminopvr.wi.api.recordings import RecordingsAPI
from aminopvr.wi.api.schedules import SchedulesAPI
import aminopvr.providers
import cherrypy
import json
import logging
import mimetypes
import os
import re
import urllib

class STBAPI( API ):
    _logger = logging.getLogger( "aminopvr.WI.API.STB" )

    @cherrypy.expose
    @API._grantAccess
    # TODO: this is too STB/provider specific
    def setChannelList( self, channelList ):
        self._logger.debug( "setChannelList( %s )" % ( channelList ) )

        try:
            channels = json.loads( channelList )
            conn     = DBConnection()

            conn.delayCommit( True )

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
    # TODO: to be removed --> should become broadcast message from renderer to controllers
    def setActiveChannel( self, channel ):
        self._logger.debug( "setActiveChannel( %s )" % ( channel ) )
        return self._createResponse( API.STATUS_SUCCESS )

    def _getChannelFromJson( self, json, channelId=-1 ):
        channel = PendingChannel.fromDict( json, channelId )
        if channel:
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
                    channelUrl              = PendingChannelUrl( urlType )
                    channelUrl.protocol     = protocol
                    channelUrl.ip           = ip
                    channelUrl.port         = port
                    channelUrl.arguments    = arguments
                    channel.addUrl( channelUrl )
        return channel

class AminoPVRAPI( API ):

    _logger = logging.getLogger( "aminopvr.WI.API" )

    stb        = STBAPI()
    channels   = ChannelsAPI()
    config     = ConfigAPI()
    controller = ControllerAPI()
    epg        = EpgAPI()
    recordings = RecordingsAPI()
    schedules  = SchedulesAPI()

    @cherrypy.expose
    @API._grantAccess
    def index( self ):
        return "Welcome to AminoPVR API"

    @cherrypy.expose
    @API._grantAccess
    # TODO: --> api/status
    def getStorageInfo( self ):
        self._logger.debug( "getStorageInfo()" )
        generalConfig = GeneralConfig( Config() )
        free, total   = getFreeTotalSpaceMb( generalConfig.recordingsPath )
        return self._createResponse( API.STATUS_SUCCESS, { "available_size": free, "total_size": total } )

    @cherrypy.expose
    @API._grantAccess
    # TODO: --> api/admin
    def activatePendingChannels( self ):
        self._logger.debug( "activatePendingChannels()" )
        conn = DBConnection()
        pendingChannels = PendingChannel.getAllFromDb( conn, includeInactive=True, includeRadio=True, tv=True )

        pendingChannelNumbers = [ channel.number for channel in pendingChannels ]

        conn.delayCommit( True )

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

        conn.delayCommit( False )

        channels      = Channel.getAllFromDb( conn, includeRadio=True, tv=True )
        channelsArray = []

        for channel in channels:
            channelJson = channel.toDict( InputStreamProtocol.HTTP, includeScrambled=False, includeHd=True )
            if channelJson:
                channelsArray.append( channelJson )
        return self._createResponse( API.STATUS_SUCCESS, channelsArray )

    @cherrypy.expose
    @API._grantAccess
    # TODO: --> api/admin
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

    @cherrypy.expose
    @API._grantAccess
    # TODO: --> api/admin
    def postLog( self, logData ):
        self._logger.debug( "postLog( %s )" % ( logData ) )
        logs = json.loads( logData )
        for log in logs:
            logger = logging.getLogger( "aminopvr.Log.%s" % ( log["module"] ) )
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
