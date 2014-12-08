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
_CHARACTERS_PER_BLOCK   = 5.5

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
        conn = DBConnection()
        if conn:
            symbols = {}
            symbols["channels"] = []

            timeBlocks      = _TIMEBLOCKS
            percentage      = 85.0 / (_TIMEBLOCKS * 3)
            now             = datetime.datetime.now()
            startTime       = getTimestamp( now ) - (getTimestamp( now ) % (15 * 60))
            endTime         = startTime + (15 * 60 * timeBlocks)
            blockOffset     = 0

            symbols["timeBlocks"] = []
            for i in range( _TIMEBLOCKS ):
                timeBlock = {}
                timeBlock["time"]       = datetime.datetime.fromtimestamp( startTime + (i * 15 * 60) ).strftime("%H:%M")
                timeBlock["blocks"]     = 3
                timeBlock["percentage"] = int( round( 3 * percentage ) )
                symbols["timeBlocks"].append( timeBlock )

            channels = Channel.getAllFromDb( conn )
            for channel in channels:
                channelDict = channel.toDict( includeScrambled=True, includeHd=True )
                if channelDict:
                    channelDict["programs"] = []
                    programs    = EpgProgram.getAllByEpgIdFromDb( conn, channel.epgId, startTime, endTime )
                    blockOffset = 0
                    for program in programs:
                        if program.endTime > startTime and program.startTime < endTime:
                            programStartTime = program.startTime
                            programEndTime   = program.endTime
                            if programStartTime < startTime:
                                programStartTime = startTime
                            if programEndTime > endTime:
                                programEndTime = endTime
                            startBlock = _calculateBlockOffset( programStartTime - startTime )
                            endBlock   = _calculateBlockOffset( programEndTime - startTime )
                            if startBlock > blockOffset:
                                blocks = startBlock - blockOffset
                                channelDict["programs"].append( { "title": "...", "blocks": blocks, "percentage": int( round( blocks * percentage ) ), "category": "Unknown" } )
                            if endBlock > blockOffset:
                                blocks      = endBlock - startBlock
                                programDict = program.toDict()

                                programDict["title"] = _truncateString( programDict["title"], blocks )
                                if "subtitle" in programDict:
                                    subtitle = program.subtitle
                                    if subtitle.find( program.title ) == 0:
                                        subtitle = subtitle[len(program.title):]
                                        if len( subtitle ) > 0 and subtitle[0] == ':':
                                            subtitle = subtitle[1:]
                                        subtitle.strip()
                                    if len( subtitle ) > 0:
                                        programDict["subtitle"] = _truncateString( subtitle, blocks )
                                    else:
                                        del programDict["subtitle"]
                                programDict["blocks"]     = blocks
                                programDict["percentage"] = int( round( blocks * percentage ) )
                                if "genres" in programDict:
                                    category = programDict["genres"][0]
                                    programDict["category"] = category.replace( "/", "_" )
                                else:
                                    programDict["category"]   = "Unknown"
                                channelDict["programs"].append( programDict )
                                blockOffset = endBlock
                    symbols["channels"].append( channelDict )
        template = Template( file=os.path.join( DATA_ROOT, "assets/webui/epg/index.html.tmpl" ), searchList=[symbols] )
        return template.respond()
