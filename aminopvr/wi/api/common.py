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

    STATUS_SUCCESS          = 0
    STATUS_FAIL             = 1
    STATUS_ARGUMENT_ERROR   = 2

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
    def _parseArguments( cls, argList=[] ):
        arguments    = []
        argumentList = argList
        for key, _ in argumentList:
            arguments.append( key )

        def decorator( target ):
            def _checkType( argType, argument ):
                status = False
                if isinstance( argument, argType ):
                    status = True
                else:
                    if argType == types.BooleanType:
                        if (type( argument ) in types.StringTypes and argument in [ "true", "True" ]) or (type( argument ) == types.IntType and argument == 1):
                            argument = True
                            status   = True
                        elif (type( argument ) in types.StringTypes and argument in [ "false", "False" ]) or (type( argument ) == types.IntType and argument == 0):
                            argument = False
                            status   = True
                    elif argType == types.IntType:
                        if type( argument ) in types.StringTypes:
                            try:
                                argument = int( argument )
                                status   = True
                            except ValueError:
                                status   = False
                    elif argType in types.StringTypes:
                        argument = str( argument )
                return ( status, argument )

            def wrapper( *args, **kwargs ):
                argList = list( args )
                if len( kwargs ) > len( arguments ):
                    cls._apiLogger.error( "_parseArguments: too many arguments: got: %d, expected: %d" % ( len( kwargs ), len( arguments ) ) )
                    return cls._createResponse( API.STATUS_ARGUMENT_ERROR, "too many arguments: got: %d, expected: %d" % ( len( kwargs ), len( arguments ) ) )
                elif len( argList ) - 1 > len( arguments ):
                    cls._apiLogger.error( "_parseArguments: too many arguments: got: %d, expected: %d" % ( len( argList ) - 1, len( arguments ) ) )
                    return cls._createResponse( API.STATUS_ARGUMENT_ERROR, "too many arguments: got: %d, expected: %d" % ( len( argList ) - 1, len( arguments ) ) )
                else:
                    for key, argType in argumentList:
                        cls._apiLogger.debug( "_parseArguments: argumentList[]: key=%s, argType=%r" % ( key, argType ) )
                    for arg in argList:
                        cls._apiLogger.debug( "_parseArguments: argList[]=%r" % ( arg ) )
                    cls._apiLogger.debug( "_parseArguments: kwargs: keys=%r, kwargs=%r" % ( kwargs.keys(), kwargs ) )

                    i = 1
                    for key, argType in argumentList:
                        argument = None
                        if i < len( argList ):
                            argument = argList[i]
                        elif key in kwargs.keys():
                            argument = kwargs[key]

                        if argument:
                            status, argument = _checkType( argType, argument )
                            if not status:
                                cls._apiLogger.error( "_parseArguments: unexpected type for key: %s: value: %s, expected: %r" % ( key, argument, argType ) )
                                return cls._createResponse( API.STATUS_ARGUMENT_ERROR, "unexpected type for key: %s: value: %s, expected: %r" % ( key, argument, argType ) )

                            if i < len( args ):
                                argList[i] = argument
                                if key in kwargs.keys():
                                    del( kwargs[key] )
                            elif key in kwargs.keys():
                                kwargs[key] = argument
                        i += 1

                    for key in kwargs.keys():
                        if key not in arguments:
                            cls._apiLogger.error( "_parseArguments: unknown argument with key: %s" % ( key ) )
                            return cls._createResponse( API.STATUS_ARGUMENT_ERROR, "unknown argument with key: %s" % ( key ) )
    
                    args = tuple( argList )
    
                return target( *args, **kwargs )
            return wrapper
        return decorator

    @classmethod
    def _acceptJson( cls, target ):
        def wrapper( *args, **kwargs ):
            if 'Content-Type' in cherrypy.request.headers:
                contentType   = cherrypy.request.headers['Content-Type']
                if contentType == "application/json":
                    contentLength = cherrypy.request.headers['Content-Length']
                    rawBody       = cherrypy.request.body.read( int( contentLength ) )
                    jsonData      = json.loads( rawBody )

                    for arg in jsonData.keys():
                        if not kwargs.has_key( arg ):
                            kwargs[arg] = jsonData[arg]
                            cls._apiLogger.debug( "_acceptJson: adding argument=%s to arguments" % ( arg ) )
                        else:
                            cls._apiLogger.warning( "_acceptJson: argument=%s already an argument" % ( arg ) )

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

    @classmethod
    def _createResponse( cls, status, data=None ):
        response = {}
        response["status"] = "unknown"
        if status == API.STATUS_SUCCESS:
            response["status"] = "success"
        elif status == API.STATUS_FAIL:
            response["status"] = "fail"
        elif status == API.STATUS_ARGUMENT_ERROR:
            response["status"] = "argument_error"
        if data:
            response["data"] = data
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps( response )
