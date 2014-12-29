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
from aminopvr.database.channel import Channel, ChannelUrl
from aminopvr.database.db import DBConnection
from aminopvr.database.epg import EpgProgram
from aminopvr.database.schedule import Schedule
from aminopvr.scheduler import Scheduler
from aminopvr.wi.api.common import API
import cherrypy
import json
import logging
import re
import types

class SchedulesAPI( API ):

    _logger = logging.getLogger( "aminopvr.WI.API.Schedules" )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments()
    def index( self ):
        return "Schedules API"

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments()
    # TODO: this is still very STB oriented --> define proper API here and in JavaScript
    def getScheduleList( self ):
        self._logger.debug( "getScheduleList()" )
        conn           = DBConnection()
        schedules      = Schedule.getAllFromDb( conn )
        schedulesArray = []
        for schedule in schedules:
            scheduleJson = schedule.toDict()
            if scheduleJson:
                schedulesArray.append( scheduleJson )
        return self._createResponse( API.STATUS_SUCCESS, schedulesArray )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("title", types.StringTypes), ("channelId", types.IntType)] )
    def getScheduleByTitleAndChannelId( self, title, channelId ):
        self._logger.debug( "getScheduleByTitleAndChannelId( title=%s, channelId=%d )" % ( title, channelId ) )
        conn        = DBConnection()
        schedule    = Schedule.getByTitleAndChannelIdFromDb( conn, title, channelId )
        if schedule:
            return self._createResponse( API.STATUS_SUCCESS, schedule.toDict() )
        else:
            return self._createResponse( API.STATUS_FAIL )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments()
    def getNumScheduledRecordings( self ):
        self._logger.debug( "getNumScheduledRecordings()" )
        scheduledRecordings = Scheduler().getScheduledRecordings()
        return self._createResponse( API.STATUS_SUCCESS, { "num_recordings": len( scheduledRecordings ) } )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("offset", types.IntType), ("count", types.IntType), ("sort", types.IntType)] )
    # TODO: this is still very STB oriented --> define proper API here and in JavaScript
    # TODO: --> this function returns recordings, so should it be part of RecordingsAPI?
    def getScheduledRecordingList( self, offset=None, count=None, sort=None ):
        self._logger.debug( "getScheduledRecordingList( offset=%s, count=%s, sort=%s )" % ( offset, count, sort ) )
        scheduledRecordings = Scheduler().getScheduledRecordings()
        scheduledRecordingsArray = []
        for scheduledRecording in scheduledRecordings:
            scheduledRecordingJson = scheduledRecording.toDict()
            if scheduledRecordingJson:
                scheduledRecordingsArray.append( scheduledRecordingJson )
        return self._createResponse( API.STATUS_SUCCESS, scheduledRecordingsArray )

    @cherrypy.expose
    @API._grantAccess
    @API._acceptJson
    @API._parseArguments( [("schedule", types.StringTypes)] )
    def getMatches( self, schedule ):
        self._logger.debug( "getMatches( schedule=%s )" % ( schedule ) )

        scheduleDict = json.loads( schedule )
        if scheduleDict:
            newSchedule = Schedule.fromDict( scheduleDict, scheduleDict["id"] )
            if newSchedule:
                matchedRecordings = Scheduler().getScheduleMatches( newSchedule )
                matchedRecordingsArray = []
                for matchedRecording in matchedRecordings:
                    matchedRecordingJson = matchedRecording.toDict()
                    if matchedRecordingJson:
                        matchedRecordingsArray.append( matchedRecordingJson )
                return self._createResponse( API.STATUS_SUCCESS, matchedRecordingsArray )
            else:
                self._logger.error( "getMatches: Unable to create new schedule from scheduleDict=%r" % ( scheduleDict ) )

                return self._createResponse( API.STATUS_FAIL, "Unable to create Schedule object" )
        self._logger.error( "getMatches: Unable to parse json=%s" % ( schedule ) )
        
        return self._createResponse( API.STATUS_FAIL, "Error parsing json" )

    @cherrypy.expose
    @API._grantAccess
    @API._acceptJson
    @API._parseArguments( [("schedule", types.StringTypes)] )
    # TODO
    def addSchedule( self, schedule ):
        self._logger.debug( "addSchedule( schedule=%s )" % ( schedule ) )
        conn         = DBConnection()
 
        scheduleDict = json.loads( schedule )
        if scheduleDict:
            newSchedule = Schedule.fromDict( scheduleDict )
 
            if newSchedule:
                if newSchedule.channelId != -1:
                    channel = Channel.getFromDb( conn, newSchedule.channelId )
                    if not channel:
                        self._logger.warning( "addSchedule: Schedule refers to non-existing channelId=%d" % ( newSchedule.channelId ) )
    
                newSchedule.addToDb( conn )
                Scheduler().requestReschedule()
    
                return self._createResponse( API.STATUS_SUCCESS, newSchedule.id )
            else:
                self._logger.error( "addSchedule: Unable to create new schedule from scheduleDict=%r" % ( scheduleDict ) )

                return self._createResponse( API.STATUS_FAIL, "Unable to create Schedule object" )

        self._logger.error( "addSchedule: Unable to parse json=%s" % ( schedule ) )

        return self._createResponse( API.STATUS_FAIL, "Error parsing json" )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("url", types.StringTypes), ("titleId", types.StringTypes), ("startTime", types.IntType), ("endTime", types.IntType), ("aa", types.StringTypes)] )
    # TODO: this is still very STB oriented --> define proper API here and in JavaScript
    def addScheduleStb( self, url, titleId, startTime, endTime, aa ):
        self._logger.debug( "addScheduleStb( url=%s, titleId=%s, startTime=%d, endTime=%d, aa=%s )" % ( url, titleId, startTime, endTime, aa ) )
        conn      = DBConnection()

        # Split title and programId
        title, programId = titleId.split( "||[", 2 )

        # Find the program we would like to record
        program   = EpgProgram.getByOriginalIdFromDb( conn, programId )
        if program:
            urlRe = re.compile( r"(?P<protocol>[a-z]{3,5}):\/\/(?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}):(?P<port>[0-9]{1,5})(?P<arguments>;.*)?" )
            urlMatch = urlRe.search( url )

            # Decode url into ip and port
            if urlMatch:
                ip   = urlMatch.group( "ip" )
                port = int( urlMatch.group( "port" ) )

                # Find channelId which uses this ip/port combination
                channelId = ChannelUrl.getChannelByIpPortFromDb( conn, ip, port )
                if channelId:
                    # Get the associated channel
                    channel = Channel.getFromDb( conn, channelId )
                    if channel:
                        # See if we already have a schedule to record this program
                        schedule = Schedule.getByTitleAndChannelIdFromDb( conn, title, channel.id )
                        if schedule:
                            timeDiff = startTime - schedule.startTime
                            if schedule.type != Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_DAY and \
                               schedule.type != Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK:
                                # If the time diff is a week, then we seem to want to record once every week 
                                if timeDiff >= (7 * 24 * 60 * 60):
                                    schedule.type = Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK
                                # If the time diff is a week, then we seem to want to record once every day 
                                elif timeDiff >= (1 * 24 * 60 * 60):
                                    schedule.type = Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_DAY
                                schedule.addToDb( conn )
                                Scheduler().requestReschedule()
                        else:
                            schedule                    = Schedule()
                            schedule.type               = Schedule.SCHEDULE_TYPE_ONCE
                            schedule.channelId          = channelId
                            schedule.startTime          = startTime
                            schedule.endTime            = endTime
                            schedule.title              = title
                            schedule.preferHd           = True
                            schedule.preferUnscrambled  = False
                            schedule.dupMethod          = Schedule.DUPLICATION_METHOD_TITLE | Schedule.DUPLICATION_METHOD_SUBTITLE
                            schedule.addToDb( conn )
                            Scheduler().requestReschedule()

                        return self._createResponse( API.STATUS_SUCCESS, schedule.id )
                    else:
                        self._logger.warning( "addSchedule: Unable to find channel with channelId=%d" % ( channelId ) )
                else:
                    self._logger.warning( "addSchedule: Unable to find channel from ip=%s, port=%d" % ( ip, port ) )
            else:
                self._logger.warning( "addSchedule: Unable to match url=%s" % ( url ) )
        else:
            self._logger.warning( "addSchedule: Unable to find recording with originalId=%s" % ( programId ) )

        return self._createResponse( API.STATUS_FAIL, "Unknown" )

    @cherrypy.expose
    @API._grantAccess
    @API._parseArguments( [("id", types.IntType)] )
    def deleteSchedule( self, id ):  # @ReservedAssignment
        self._logger.debug( "deleteSchedule( id=%s )" % ( id ) )

        conn     = DBConnection()
        schedule = Schedule.getFromDb( conn, int( id ) )
        if schedule:
            schedule.deleteFromDb( conn )
            Scheduler().requestReschedule()
            return self._createResponse( API.STATUS_SUCCESS )
        else:
            self._logger.error( "deleteSchedule: Unable to find schedule with id=%d" % ( int( id ) ) )

        return self._createResponse( API.STATUS_FAIL )

    @cherrypy.expose
    @API._grantAccess
    @API._acceptJson
    @API._parseArguments( [("id", types.IntType), ("schedule", types.StringTypes)] )
    def changeSchedule( self, id, schedule ):  # @ReservedAssignment
        self._logger.debug( "changeSchedule( id=%s, schedule=%s )" % ( id, schedule ) )

        scheduleDict = json.loads( schedule )
        if scheduleDict:
            conn         = DBConnection()
            currSchedule = Schedule.getFromDb( conn, int( id ) )
            if currSchedule:
                newSchedule = Schedule.fromDict( scheduleDict, int( id ) )
                if newSchedule.channelId != -1:
                    channel = Channel.getFromDb( conn, newSchedule.channelId )
                    if not channel:
                        self._logger.warning( "changeSchedule: Schedule refers to non-existing channelId=%d" % ( newSchedule.channelId ) )

                if currSchedule != newSchedule:
                    newSchedule.addToDb( conn )
                    Scheduler().requestReschedule()
                else:
                    self._logger.warning( "changeSchedule: no changes in Schedule" )

                return self._createResponse( API.STATUS_SUCCESS )
            else:
                self._logger.error( "changeSchedule: Unable to find schedule with id=%d" % ( int( id ) ) )
        else:
            self._logger.error( "changeSchedule: Unable to create dictionary from schedule=%s" % ( schedule ) )

        return self._createResponse( API.STATUS_FAIL )
