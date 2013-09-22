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
from aminopvr.config import GeneralConfig, Config
import cherrypy
import json
import logging
import socket
import struct
import types

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
