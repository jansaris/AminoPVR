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
from aminopvr.const import DATA_ROOT
from aminopvr.db import DBConnection
from aminopvr.providers.glashart.config import glashartConfig
from aminopvr.providers.glashart.page import PageSymbol
from cherrypy.lib.static import serve_fileobj
import aminopvr.wi
import cherrypy
import json
import logging
import os
import urllib

class WebInterface( aminopvr.wi.WebInterface ):
    _logger = logging.getLogger( "aminopvr.providers.glashart.WI" )

    @cherrypy.expose
    def index( self ):
        raise cherrypy.HTTPRedirect( "index.xhtml" )

    @cherrypy.expose
    def index_xhtml( self ):
        return self._serveDBContent( "index.xhtml", "application/xhtml+xml" )

    @cherrypy.expose
    def style_css( self ):
        return self._serveDBContent( "style.css", "text/css" )

    @cherrypy.expose
    def code_js( self ):
        return self._serveDBContent( "code.js", "application/javascript" )

    @cherrypy.expose
    def api_js( self ):
        conn = DBConnection()
        if conn:
            symbols  = PageSymbol.getAllFromDb( conn )
            template = Template( file=os.path.join( DATA_ROOT, "assets/js/api.js.tmpl" ), searchList=[symbols] )
            cherrypy.response.headers["Content-Type"] = "application/javascript"
            return template.respond()
        return self._serveDBContent( "api.js", "application/javascript" )

    @cherrypy.expose
    def vodinfo( self, *args, **kwargs ):
        self._logger.debug( "vodinfo( %s, %s )" )
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return json.dumps( { "length": 0, "available_length": 0 } )

    @cherrypy.expose
    def stbinfo( self, *args, **kwargs ):
        self._logger.debug( "stbinfo( %s, %s )" % ( str( args ), str( kwargs ) ) )
        method = cherrypy.request.method.upper()
        url    = glashartConfig.iptvBaseUrl + "/stbinfo"
        if len( list( args ) ) > 0:
            url = url + "/" + '/'.join( list( args ) )
        return self._serveRemoteContent( url, method, kwargs )

    @cherrypy.expose
    def rckey_xhtml( self, *args, **kwargs ):
        self._logger.debug( "rckey_xhtml( %s, %s )" )
        method = cherrypy.request.method.uppper()
        url    = glashartConfig.iptvBaseUrl + "/rckey.xhtml"
        return self._serveRemoteContent( url, method, kwargs )

    @cherrypy.expose
    def epgdata( self, *args, **kwargs ):
        self._logger.debug( "epgdata( %s, %s )" % ( str( args ), str( kwargs ) ) )
        method = cherrypy.request.method.upper()
        url    = glashartConfig.epgDataPath + "/" + '/'.join( list( args ) )
        return self._serveRemoteContent( url, method, kwargs )

    @cherrypy.expose
    def last_update_txt( self, *args, **kwargs ):
        self._logger.debug( "last_update_txt( %s, %s )" % ( str( args ), str( kwargs ) ) )
        method = cherrypy.request.method.upper()
        url    = glashartConfig.iptvBaseUrl + "/" + glashartConfig.tvmenuPath + "/last-update.txt"
        return self._serveRemoteContent( url, method, kwargs )

    @cherrypy.expose
    def images( self, *args, **kwargs ):
        self._logger.debug( "images( %s, %s )" % ( str( args ), str( kwargs ) ) )

        url = glashartConfig.iptvBaseUrl + "/" + glashartConfig.tvmenuPath + "/images/" + '/'.join( list( args ) )
        return self._serveRemoteContent( url )

    @cherrypy.expose
    def api( self, *args, **kwargs ):
        self._logger.debug( "api( %s, %s )" % ( str( args ), str( kwargs ) ) )
        method = cherrypy.request.method.upper()
        url    = glashartConfig.iptvBaseUrl + "/api"
        if len( list( args ) ) > 0:
            url = url + "/" + '/'.join( list( args ) )

        # API call requests are in POST method, but remote server requires the GET parameters
        # to be part of the 'GET' query
        # So, get the requested query string and remove those keys from the GET+POST parameter list 
        if method == "POST":
            queryString = cherrypy.request.query_string
            url = url + "?" + queryString
            arguments = {}
            for item in queryString.split( '&' ):
                itemArray = item.split( '=' )
                if len( itemArray ) == 2:
                    arguments[itemArray[0]] = itemArray[1]
                else:
                    arguments[itemArray[0]] = ""
            for key in arguments:
                if key in kwargs:
                    del kwargs[key]
            self._logger.debug( "queryString=%s; kwargs=%s" % ( queryString, str( kwargs ) ) )
        return self._serveRemoteContent( url, method, kwargs )

    def _serveDBContent( self, filename, contentType = None ):
        conn = DBConnection()
        try:
            result = conn.execute( "SELECT content FROM glashart_pages WHERE page=?", [filename] )
            if result:
                row = result.fetchone()
                if contentType:
                    cherrypy.response.headers["Content-Type"] = contentType
                return row["content"]
            else:
                raise cherrypy.HTTPError( 404 )
        except:
            raise cherrypy.HTTPError( 500 )

    def _serveRemoteContent( self, url, method="GET", args={} ):
        if method == "GET" and len( args ) > 0:
            url = url + "?" + urllib.urlencode( args )
        content, code, mime = aminopvr.tools.getPage( url, None, method=method, args=args )
        if code == 200:
            if "Content-Encoding: x-gzip" in str( mime ):
                cherrypy.response.headers["Content-Encoding"]= "x-gzip"
            return serve_fileobj( content, content_type=mime.gettype() )
        else:
            raise cherrypy.HTTPError( code )
