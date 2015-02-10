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
from aminopvr.database.recording import Recording
from aminopvr.scheduler import Scheduler
from aminopvr.wi.api.common import API
import cherrypy
import logging
import types

class RecordingsAPI( API ):

    _logger = logging.getLogger( "aminopvr.WI.API.Recordings" )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments()
    def index( self ):
        return "Recordings API"

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments()
    def getNumRecordings( self ):
        self._logger.debug( "getNumRecordings()" )
        conn = DBConnection()
        return self._createResponse( API.STATUS_SUCCESS, { "num_recordings": Recording.getNumRecordingsFromDb( conn ) } )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("offset", types.IntType), ("count", types.IntType), ("sort", types.IntType)] )
    # TODO: this is still very STB oriented --> define proper API here and in JavaScript
    def getRecordingList( self, offset=None, count=None, sort=None ):
        self._logger.debug( "getRecordingList( offset=%s, count=%s, sort=%s )" % ( offset, count, sort ) )

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
    @API._parseArguments( [("id", types.IntType)] )
    # TODO: this is still very STB oriented --> define proper API here and in JavaScript
    def getRecordingById( self, id ):  # @ReservedAssignment
        self._logger.debug( "getRecordingById( id=%s )" % ( id ) )

        conn        = DBConnection()
        recording   = Recording.getFromDb( conn, id )
        if recording:
            return self._createResponse( API.STATUS_SUCCESS, recording.toDict() )
        else:
            return self._createResponse( API.STATUS_FAIL );

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("id", types.IntType), ("rerecord", types.BooleanType)] )
    def deleteRecording( self, id, rerecord=False ):  # @ReservedAssignment
        self._logger.debug( "deleteRecording( id=%s, rerecord=%s )" % ( id, rerecord ) )
        conn        = DBConnection()
        recording   = Recording.getFromDb( conn, id )
        if recording:
            recording.deleteFromDb( conn, rerecord )
            if rerecord:
                Scheduler().requestReschedule()
            return self._createResponse( API.STATUS_SUCCESS )
        else:
            self._logger.warning( "deleteRecording: recording with id=%d does not exist" % ( id ) )
        return self._createResponse( API.STATUS_FAIL )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("id", types.IntType)] )
    def getRecordingMarker( self, id ):  # @ReservedAssignment
        self._logger.debug( "getRecordingMarker( id=%s )" % ( id ) )
        conn      = DBConnection()
        recording = Recording.getFromDb( conn, id )
        if recording:
            return self._createResponse( API.STATUS_SUCCESS, { "marker": recording.marker / 1024 / 1024 } )
        return self._createResponse( API.STATUS_FAIL )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("id", types.IntType), ("marker", types.IntType)] )
    def setRecordingMarker( self, id, marker ):  # @ReservedAssignment
        self._logger.debug( "setRecordingMarker( id=%s, marker=%s )" % ( id, marker ) )
        conn      = DBConnection()
        recording = Recording.getFromDb( conn, id )
        if recording:
            recording.marker = marker * 1024 * 1024
            self._logger.warn( "setRecordingMarker: marker=%d" % ( recording.marker ) )
            recording.addToDb( conn )
            return self._createResponse( API.STATUS_SUCCESS )
        return self._createResponse( API.STATUS_FAIL )
