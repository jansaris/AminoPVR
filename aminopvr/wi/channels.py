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
from aminopvr.database.db import DBConnection
from aminopvr.database.channel import Channel
from aminopvr.input_stream import InputStreamProtocol, InputStreamAbstract
from aminopvr.resource_monitor import Watchdog
from aminopvr.tsdecrypt import IsTsDecryptSupported
from aminopvr.wi.api.common import API
import cherrypy
import logging
import types
import uuid

BUFFER_SIZE = 40 * 188

class Channels( API ):
    _logger = logging.getLogger( "aminopvr.WI.Channels" )

    @cherrypy.expose
    @API._grantAccess
    def default( self, *args, **kwargs ):
        self._logger.debug( "default( %s, %s )" % ( str( args ), str( kwargs ) ) )

        #for header in cherrypy.request.headers:
        #    self._logger.debug( "default: header: %s: %s" % ( header, cherrypy.request.headers[header] ) )

        API._parseArguments( [("includeScrambled", types.BooleanType), ("includeHd", types.BooleanType)] )

        includeScrambled = False
        includeHd        = True
        if "includeScrambled" in kwargs:
            includeScrambled = kwargs["includeScrambled"]
        if "includeHd" in kwargs:
            includeHd        = kwargs["includeHd"]

        conn        = DBConnection()
        channelId   = list( args )[0]
        channel     = Channel.getFromDb( conn, channelId )
        if channel:
            url = None

            protocol = InputStreamProtocol.HTTP
            if IsTsDecryptSupported():
                protocol         = InputStreamProtocol.TSDECRYPT
                includeScrambled = True

            if includeHd and "hd" in channel.urls.keys() and ( includeScrambled or not channel.urls["hd"].scrambled ):
                url = channel.urls["hd"]
            elif includeHd and "hd+" in channel.urls.keys() and ( includeScrambled or not channel.urls["hd+"].scrambled ):
                url = channel.urls["hd+"]
            elif "sd" in channel.urls.keys() and ( includeScrambled or not channel.urls["sd"].scrambled ):
                url = channel.urls["sd"]

            if url:
                inputStream = InputStreamAbstract.createInputStream( protocol, url )
                if inputStream.open():
                    watchdogId = uuid.uuid1()
                    def watchdogTimeout():
                        self._logger.warning( "default: watchdog timed out; close stream; remove watchdog %s" % ( watchdogId ) )
                        inputStream.close()
                        Watchdog().remove( watchdogId )
                    Watchdog().add( watchdogId, watchdogTimeout )
                    Watchdog().kick( watchdogId, 10 )
                    cherrypy.response.headers[ "Content-Type" ] = "video/mp2t"
                    def content():
                        self._logger.info( "default: opened stream" )
                        Watchdog().kick( watchdogId, 10 )
                        data = inputStream.read( BUFFER_SIZE )
                        while len( data ) > 0:
                            yield data
                            Watchdog().kick( watchdogId, 10 )
                            data = inputStream.read( BUFFER_SIZE )
                        self._logger.info( "default: EOS" )
                        inputStream.close()
                        Watchdog().remove( watchdogId )

                    return content()
                else:
                    return self._createResponse( API.STATUS_FAIL )
            else:
                return self._createResponse( API.STATUS_FAIL )
        else:
            return self._createResponse( API.STATUS_FAIL )
    default._cp_config = { "response.stream": True } 
