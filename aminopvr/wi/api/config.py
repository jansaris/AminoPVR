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
from aminopvr.wi.api.common import API
import cherrypy
import logging

class ConfigAPI( API ):
    _logger = logging.getLogger( "aminopvr.WI.ConfigAPI")

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments()
    def getGeneralConfig( self ):
        generalConfig = GeneralConfig( Config() )
        return self._createResponse( API.STATUS_SUCCESS, generalConfig.toDict() )
