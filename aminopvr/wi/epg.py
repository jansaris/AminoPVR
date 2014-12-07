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

class WebUIEpg( object ):
    _logger = logging.getLogger( "aminopvr.WI.WebUI.Epg" )
    
    @cherrypy.expose
    def index( self ):
        conn = DBConnection()
        if conn:
            symbols = {}
            symbols["channels"] = []

            timeBlocks      = 12
            percentage      = 85.0 / (timeBlocks * 3)
            now             = datetime.datetime.now()
            startTime       = getTimestamp( now ) - (getTimestamp( now ) % (15 * 60))
            endTime         = startTime + (15 * 60 * timeBlocks)
            lastStartTime   = startTime

            channels = Channel.getAllFromDb( conn )
            for channel in channels:
                channelDict = channel.toDict( includeScrambled=True, includeHd=True )
                if channelDict:
                    channelDict["programs"] = []
                    programs = EpgProgram.getAllByEpgIdFromDb( conn, channel.epgId, startTime, endTime )
                    for program in programs:
                        if program.endTime > startTime and program.startTime < endTime:
                            if program.startTime > lastStartTime:
                                blocks = (program.startTime - lastStartTime) / (5 * 60)
                                channelDict["programs"].append( { "title": "NO DATA", "blocks": int( blocks ), "percentage": int( blocks * percentage ), "category": "Unknown" } )
                            programStartTime = program.startTime
                            programEndTime   = program.endTime
                            if programStartTime < startTime:
                                programStartTime = startTime
                            if programEndTime > endTime:
                                programEndTime = endTime
                            blocks = (programEndTime - programStartTime) / (5 * 60)
                            if blocks < 1.0:
                                blocks = 1.0
                            titleLength = len( program.title )
                            programDict = program.toDict()
                            if titleLength > int(blocks * 4):
                                lastChar = int(blocks * 4) - 3;
                                if lastChar <= 0:
                                    programDict["title"] = "..."
                                else:
                                    programDict["title"] = "%s..." % ( programDict["title"][:lastChar])
                            programDict["blocks"]     = int(blocks)
                            programDict["percentage"] = int(blocks * percentage)
                            programDict["category"]   = "Action"
                            channelDict["programs"].append( programDict )
                            lastStartTime = programEndTime
                    symbols["channels"].append( channelDict )
        symbols["timeBlocks"] = timeBlocks
        template = Template( file=os.path.join( DATA_ROOT, "assets/webui/epg/index.html.tmpl" ), searchList=[symbols] )
        return template.respond()
