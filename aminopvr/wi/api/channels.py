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
from aminopvr.channel import Channel, ChannelUrl
from aminopvr.db import DBConnection
from aminopvr.input_stream import InputStreamProtocol
from aminopvr.tsdecrypt import IsTsDecryptSupported
from aminopvr.wi.api.common import API
import cherrypy
import logging
import types

class ChannelsAPI( API ):

    _logger = logging.getLogger( "aminopvr.WI.API.Channels" )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments()
    def index( self ):
        return "Channels API"

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments()
    def getNumChannels( self ):
        self._logger.debug( "getNumChannels()" )
        conn = DBConnection()
        return self._createResponse( API.STATUS_SUCCESS, { "num_channels": Channel.getNumChannelsFromDb( conn ) } )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("tv", types.BooleanType), ("radio", types.BooleanType), ("unicast", types.BooleanType), ("includeScrambled", types.BooleanType), ("includeHd", types.BooleanType)] )
    def getChannelList( self, tv=True, radio=False, unicast=True, includeScrambled=False, includeHd=True ):
        self._logger.info( "getChannelList( tv=%s, radio=%s, unicast=%s, includeScrambled=%s, includeHd=%s )" % ( tv, radio, unicast, includeScrambled, includeHd ) )
        conn          = DBConnection()
        channels      = Channel.getAllFromDb( conn, includeRadio=radio, tv=tv )
        channelsArray = []

        protocol = InputStreamProtocol.HTTP
        if IsTsDecryptSupported():
            protocol         = InputStreamProtocol.TSDECRYPT
            includeScrambled = True
        elif not unicast:
            protocol         = InputStreamProtocol.MULTICAST

        for channel in channels:
            channelJson = channel.toDict( protocol, includeScrambled, includeHd )
            if channelJson:
                channelsArray.append( channelJson )
        return self._createResponse( API.STATUS_SUCCESS, channelsArray )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("ip", types.StringTypes), ("port", types.IntType)] )
    def getChannelByIpPort( self, ip, port ):
        self._logger.debug( "getChannelByIpPort( ip=%s, port=%d )" % ( ip, port ) )
        conn      = DBConnection()
        channelId = ChannelUrl.getChannelByIpPortFromDb( conn, ip, int( port ) )
        if channelId:
            channel = Channel.getFromDb( conn, channelId )
            if channel:
                return self._createResponse( API.STATUS_SUCCESS, channel.toDict() )
        return self._createResponse( API.STATUS_FAIL )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("unicast", types.BooleanType), ("includeScrambled", types.BooleanType), ("includeHd", types.BooleanType)] )
    def createM3U( self, unicast=True, includeScrambled=False, includeHd=True ):
        self._logger.info( "createM3U( unicast=%s, includeScrambled=%s, includeHd=%s )" % ( unicast, includeScrambled, includeHd ) )
        conn     = DBConnection()
        channels = Channel.getAllFromDb( conn )

        protocol = InputStreamProtocol.HTTP
        if not unicast:
            protocol = InputStreamProtocol.MULTICAST

        m3u = "#EXTM3U\n"
        for channel in channels:
            m3u += channel.toM3UEntry( protocol, includeScrambled, includeHd )

        cherrypy.response.headers["Content-Type"] = "text/plain"
        return m3u
