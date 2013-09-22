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
from aminopvr.channel import Channel
from aminopvr.db import DBConnection
from aminopvr.epg import EpgProgram
from aminopvr.wi.api.common import API
import cherrypy
import logging

class EpgAPI( API ):

    _logger = logging.getLogger( "aminopvr.WI.API.Epg" )

    @cherrypy.expose
    @API._grantAccess
    def index( self ):
        return "Epg API"

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
    def getEpgProgramByOriginalId( self, originalId ):
        self._logger.debug( "getEpgProgramByOriginalId( originalId=%s )" % ( originalId ) )
        conn        = DBConnection()
        epgProgram  = EpgProgram.getByOriginalIdFromDb( conn, originalId )
        if epgProgram:
            return self._createResponse( API.STATUS_SUCCESS, epgProgram.toDict() )
        else:
            return self._createResponse( API.STATUS_FAIL )

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
