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
from Cheetah.Template import Template
from aminopvr import const
from aminopvr.const import DATA_ROOT
from aminopvr.db import DBConnection
from aminopvr.wi.api import AminoPVRWI, AminoPVRAPI, AminoPVRRecordings
from cherrypy.lib.static import serve_file, serve_fileobj
import aminopvr.providers
import cherrypy
import cherrypy.lib.auth_basic
import json
import logging
import os
import sqlite3
import urllib

_logger = logging.getLogger( "aminopvr.WI" )

class WebUI( object ):
    _logger = logging.getLogger( "aminopvr.WI.WebUI" )

    @cherrypy.expose
    def index( self ):
        template = Template( file=os.path.join( DATA_ROOT, "assets/webui/index.html.tmpl" ) )
        return template.respond()


class WebInterface( object ):
    api         = AminoPVRAPI()
    recordings  = AminoPVRRecordings()
    aminopvr    = AminoPVRWI()
    webui       = WebUI()


def stopWebserver():
    _logger.warning( "Stopping CherryPy Engine" )
    cherrypy.engine.stop()

def initWebserver( serverPort=8080 ):

    def http_error_401_hander( status, message, traceback, version ):
        """ Custom handler for 401 error """
        if status != "401 Unauthorized":
            _logger.error( u"CherryPy caught an error: %s %s" % ( status, message ) )
            _logger.debug( traceback )
        return r'''
<html>
    <head>
        <title>%s</title>
    </head>
    <body>
        <br/>
        <font color="#0000FF">Error %s: You need to provide a valid username and password.</font>
    </body>
</html>
''' % ( 'Access denied', status )

    def http_error_404_hander( status, message, traceback, version ):
        """ Custom handler for 404 error, redirect back to main page """
        _logger.warning( "File not found (404): %s" % ( cherrypy.url() ) )
        return r'''
<html>
    <head>
        <title>404</title>
        <script type="text/javascript" charset="utf-8">
          <!--
          location.href = "%s"
          //-->
        </script>
    </head>
    <body>
        <br/>
    </body>
</html>
''' % '/aminopvr'

    options = {
        'host':      '0.0.0.0',
        'port':      serverPort,
        'username':  'test',
        'password':  'pass',
        'web_root':  '/',
        'data_root': const.DATA_ROOT
    }

    options_dict = {
        'server.socket_port': options['port'],
        'server.socket_host': options['host'],
        'log.screen':         False,
        'error_page.401':     http_error_401_hander,
        'error_page.404':     http_error_404_hander,
    }

    _logger.info( "Starting AminoPVR on http://%s:%i/" % ( options['host'], options['port'] ) )
    cherrypy.config.update( options_dict )

    conf = {
        '/': {
            'tools.staticdir.root': options['data_root'],
            'tools.encode.on': True,
            'tools.encode.encoding': 'utf-8'
        },
        '/assets/images': {
            'tools.staticdir.on':  True,
            'tools.staticdir.dir': 'assets/images'
        },
        '/assets/js':     {
            'tools.staticdir.on':  True,
            'tools.staticdir.dir': 'assets/js'
        },
        '/assets/css':    {
            'tools.staticdir.on':  True,
            'tools.staticdir.dir': 'assets/css'
        },
        '/assets/webui/js':     {
            'tools.staticdir.on':  True,
            'tools.staticdir.dir': 'assets/webui/js'
        },
        '/assets/webui/css':    {
            'tools.staticdir.on':  True,
            'tools.staticdir.dir': 'assets/webui/css'
        },
    }

    webInterface = aminopvr.providers.webInterface
    if not webInterface:
        webInterface = WebInterface

    app = cherrypy.tree.mount( webInterface(), options['web_root'], conf )

    # auth
    if options['username'] != "" and options['password'] != "":
        checkpassword = cherrypy.lib.auth_basic.checkpassword_dict( { options['username']: options['password'] } )
        app.merge( {
            '/': {
                'tools.auth_basic.on':            True,
                'tools.auth_basic.realm':         'AminoPVR',
                'tools.auth_basic.checkpassword': checkpassword
            },
            '/api': {
                'tools.auth_basic.on':            False
            },
            '/recordings': {
                'tools.auth_basic.on':            False
            },
            '/aminopvr': {
                'tools.auth_basic.on':            True,
                'tools.auth_basic.realm':         'AminoPVR',
                'tools.auth_basic.checkpassword': checkpassword
            },
            '/aminopvr/api': {
                'tools.auth_basic.on':            False
            },
            '/aminopvr/recordings': {
                'tools.auth_basic.on':            False
            },
        } )

    if aminopvr.providers.setupWebInterface:
        aminopvr.providers.setupWebInterface( app )

    cherrypy.server.start()
    cherrypy.server.wait()
