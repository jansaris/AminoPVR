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
from aminopvr.channel import Channel
from aminopvr.const import DATA_ROOT
from aminopvr.db import DBConnection
from aminopvr.epg import EpgProgram
from aminopvr.tools import getTimestamp
import cherrypy
import datetime
import logging
import os

_logger = logging.getLogger( "aminopvr.WI" )

_TIMEBLOCKS             = 12
_TIMEBLOCK_LENGTH       = 5
_CHARACTERS_PER_BLOCK   = 100#5.5

def _calculateBlockOffset( timestamp ):
    offset = timestamp / (_TIMEBLOCK_LENGTH * 60.0)
    return int( round( offset ) )

def _truncateString( string, blocks ):
    limit = int( round( (((blocks - 1) * _CHARACTERS_PER_BLOCK) + (_CHARACTERS_PER_BLOCK / 2.0)) ) )
    if len( string ) > limit:
        string = "%s..." % ( string[:limit - 3] )
    return string

class WebUIEpg( object ):
    _logger = logging.getLogger( "aminopvr.WI.WebUI.Epg" )
    
    @cherrypy.expose
    def index( self ):
        template = Template( file=os.path.join( DATA_ROOT, "assets/webui/epg/index.html.tmpl" ) )
        return template.respond()
