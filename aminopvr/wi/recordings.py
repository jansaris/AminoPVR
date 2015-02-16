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
from aminopvr.database.db import DBConnection
from aminopvr.database.recording import Recording
from aminopvr.wi.api.common import API
from cherrypy.lib.static import serve_file
import cherrypy
import logging
import mimetypes
import os.path

class Recordings( API ):
    _logger = logging.getLogger( "aminopvr.WI.Recordings" )
    @cherrypy.expose
    @API._grantAccess
    def default( self, *args, **kwargs ):
        self._logger.debug( "default( %s, %s )" % ( str( args ), str( kwargs ) ) )

#         for header in cherrypy.request.headers:
#             self._logger.info( "default: header: %s: %s" % ( header, cherrypy.request.headers[header] ) )

        conn        = DBConnection()
        recordingId = list( args )[0]
        recording   = Recording.getFromDb( conn, recordingId )
        if recording:
            generalConfig = GeneralConfig( Config() )
            filename      = os.path.join( generalConfig.recordingsPath, recording.filename )
#            BUF_SIZE      = 16 * 1024

            if os.path.exists( filename ):
#                 f = open( filename, 'rb' )
#                 cherrypy.response.headers[ "Content-Type" ]   = mimetypes.guess_type( filename )[0]
#                 cherrypy.response.headers[ "Content-Length" ] = os.path.getsize( filename )
                return serve_file( os.path.abspath( filename ), content_type=mimetypes.guess_type( filename )[0] )
#                 def content():
#                     data = f.read( BUF_SIZE )
#                     while len( data ) > 0:
#                         yield data
#                         data = f.read( BUF_SIZE )
# 
#                 return content()
            else:
                return self._createResponse( API.STATUS_FAIL )
        else:
            return self._createResponse( API.STATUS_FAIL )
#    default._cp_config = { "response.stream": True } 
