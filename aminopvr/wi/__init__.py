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
from aminopvr.db import DBConnection
from aminopvr.wi.api import AminoPVRWI
from cherrypy.lib.static import serve_file, serve_fileobj
import aminopvr
import aminopvr.providers
import cherrypy
import cherrypy.lib.auth_basic
import json
import logging
import os
import sqlite3
import urllib

class WebInterface( object ):

    _logger = logging.getLogger( "aminopvr.WI" )

    aminopvr = AminoPVRWI()

def initWebserver( serverPort=8080 ):

    def http_error_401_hander( status, message, traceback, version ):
        """ Custom handler for 401 error """
        if status != "401 Unauthorized":
            aminopvr.logger.error( u"CherryPy caught an error: %s %s" % ( status, message ) )
            aminopvr.logger.debug( traceback )
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
''' % '/'

    options = {
        'host':      '0.0.0.0',
        'port':      int( serverPort ),
        'username':  'test',
        'password':  'pass',
        'web_root':  '/',
        'data_root': os.path.dirname( os.path.abspath( __file__ ) ) + "/../../"
    }

    options_dict = {
        'server.socket_port': options['port'],
        'server.socket_host': options['host'],
        'log.screen':         False,
        'error_page.401':     http_error_401_hander,
        'error_page.404':     http_error_404_hander,
    }

    protocol = "http"

    aminopvr.logger.info( u"Starting AminoPVR on " + protocol + "://" + str(options['host']) + ":" + str(options['port']) + "/" )
    cherrypy.config.update( options_dict )

    conf = {
        '/': {
            'tools.staticdir.root': options['data_root'],
            'tools.encode.on': True,
            'tools.encode.encoding': 'utf-8',
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
        } )


    cherrypy.server.start()
    cherrypy.server.wait()
