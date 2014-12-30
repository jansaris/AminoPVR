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
from aminopvr.wi.api.common import API
import cherrypy
import logging
import os
import types

_logger = logging.getLogger( "aminopvr.WI.WebUI" )

class WebUI( object ):
    _logger = logging.getLogger( "aminopvr.WI.WebUI" )

    @cherrypy.expose
    def index( self ):
        template = Template( file=os.path.join( const.DATA_ROOT, "assets/webui/index.html.tmpl" ) )
        return template.respond()

    @cherrypy.expose
    def epg( self ):
        template = Template( file=os.path.join( const.DATA_ROOT, "assets/webui/epg.html.tmpl" ) )
        return template.respond()

    @cherrypy.expose
    def recordings( self ):
        template = Template( file=os.path.join( const.DATA_ROOT, "assets/webui/recordings.html.tmpl" ) )
        return template.respond()

    @cherrypy.expose
    def schedules( self ):
        template = Template( file=os.path.join( const.DATA_ROOT, "assets/webui/schedules.html.tmpl" ) )
        return template.respond()

    @cherrypy.expose
    @API._parseArguments( [("searchQuery", types.StringTypes), ("where", types.StringTypes)] )
    def search( self, searchQuery="", where="" ):
        symbols = {}
        symbols["searchQuery"] = searchQuery
        symbols["where"]       = where
        symbols["title"]       = ""
        template = Template( file=os.path.join( const.DATA_ROOT, "assets/webui/search.html.tmpl" ), searchList=symbols )
        return template.respond()

    @cherrypy.expose
    @API._parseArguments()
    def status( self, searchQuery="", where="" ):
        symbols = {}
        template = Template( file=os.path.join( const.DATA_ROOT, "assets/webui/status.html.tmpl" ), searchList=symbols )
        return template.respond()
