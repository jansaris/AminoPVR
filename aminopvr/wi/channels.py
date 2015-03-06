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
from aminopvr.input_stream import InputStreamProtocol
from aminopvr.tsdecrypt import IsTsDecryptSupported
from aminopvr.virtual_tuner import VirtualTuner
from aminopvr.wi.api.common import API
import cherrypy
import logging
import types
import uuid

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
                tuner = VirtualTuner.getTuner( url, protocol )
                if tuner:
                    listenerId = uuid.uuid1()
                    tuner.addListener( listenerId )
                    cherrypy.response.headers["Content-Type"] = "video/mp2t"
                    def content():
                        self._logger.info( "default: opened tuner" )
                        data = tuner.read( listenerId )
                        while data and len( data ) > 0:
                            yield data
                            data = tuner.read( listenerId )
                        self._logger.info( "default: EOS" )
                        tuner.removeListener( listenerId )
 
                    return content()
                else:
                    return self._createResponse( API.STATUS_FAIL )
            else:
                return self._createResponse( API.STATUS_FAIL )
        else:
            return self._createResponse( API.STATUS_FAIL )
    default._cp_config = { "response.stream": True } 
