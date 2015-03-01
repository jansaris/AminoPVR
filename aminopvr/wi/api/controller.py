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
from aminopvr.wi.api.common import API
from aminopvr.wi.controller import Controller
import cherrypy
import json
import logging
import types

class ControllerAPI( API ):
    _logger = logging.getLogger( "aminopvr.WI.ControllerAPI" )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("type", types.IntType)] )
    def init( self, type=0 ):       # @ReservedAssignment - API needs this symbolname
        self._logger.debug( "init( type=%d )" % ( type ) )
        controller = Controller()
        id_        = controller.addListener( cherrypy.request.remote.ip, type )
        self._logger.warning( "init: added listener with id=%d for ip=%s and type=%d" % ( id_, cherrypy.request.remote.ip, type ) )
        # Send a message to the requester if it is a RENDERER to set the channel list
        if type == Controller.TYPE_RENDERER:
            if controller.sendMessage( id_, cherrypy.request.remote.ip, type, { "type": "command", "data": { "command": "setChannelList" } } ):
                self._logger.warning( "init: send message to self request channel list" )
            else:
                self._logger.error( "init: failed to send message to self" )
            for header in cherrypy.request.headers:
                self._logger.info( "init: listener header: %s: %s" % ( header, cherrypy.request.headers[header] ) )
        return self._createResponse( API.STATUS_SUCCESS, { "id": id_ } )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("id", types.IntType)] )
    def poll( self, id=-1 ):    # @ReservedAssignment - API needs this symbolname
        self._logger.debug( "poll( id=%d )" % ( id ) )
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
    @API._parseArguments( [("fromId", types.IntType), ("toId", types.IntType), ("message", types.StringTypes)] )
    def sendMessage( self, fromId, toId, message ):
        self._logger.debug( "sendMessage( fromId=%d, toId=%d, message=%s )" % ( fromId, toId, message ) )
        controller  = Controller()
        if not controller.isListener( fromId ):
            return self._createResponse( API.STATUS_FAIL, { "message": "Listener with id=%d is not registered" % ( fromId ) } )
        if not controller.isListener( toId ):
            return self._createResponse( API.STATUS_FAIL, { "message": "Listener with id=%d is not registered" % ( toId ) } )
        if controller.sendMessageToId( fromId, toId, json.loads( message ) ):
            return self._createResponse( API.STATUS_SUCCESS, None )
        return self._createResponse( API.STATUS_FAIL, { "message": "Couldn't send message from %d to %d" % ( fromId, toId ) } )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments()
    def getListenerList( self ):
        controller = Controller()
        listeners  = controller.getListeners()
        return self._createResponse( API.STATUS_SUCCESS, listeners )
    
    @classmethod
    def notifyShutdown( cls ):
        cls._logger.info( "notifyShutdown" )
        controller = Controller()
        controller.broadcastMessage( { "type": "notification", "data": { "command": "shutdown" } } )
