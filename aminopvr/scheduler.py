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
from aminopvr.channel import Channel
from aminopvr.db import DBConnection
from aminopvr.epg import EpgProgram, RecordingProgram
from aminopvr.input_stream import InputStreamProtocol
from aminopvr.recorder import Recorder
from aminopvr.recording import Recording, OldRecording, RecordingState
from aminopvr.schedule import Schedule
from aminopvr.timer import Timer
from aminopvr.tools import Singleton
import datetime
import logging
import threading
import time

class Scheduler( threading.Thread ):
    """
    Singleton class that takes care of the recording schedule.
    On a 'reschedule' all active schedules are checked what to record

    It holds a list of timers ('timer.Timer') each representing a 'recording.Recording' that starts
    and/or finishes in the future. After a reschedule, active timers should be updated rather than
    removed and recreated. If recording of a new 'recording.Recording' should have already been
    started, the timer should immediately fire with a start event.

    TODO:
    - Actually do something with the result of 'reschedule'
    """
    __metaclass__ = Singleton

    _lock   = threading.Lock()
    _logger = logging.getLogger( "aminopvr.Scheduler" )

    def __init__( self ):
        threading.Thread.__init__( self )

        self._logger.debug( "Scheduler.__init__()" )

        self._running   = True
        self._timers    = {}
        self._idCounter = 0

    def stop( self, timeout=10 ):
        self._logger.warning( "Stopping scheduler and ending all timers" )
        self._running = False
        self.join()

    def run( self ):
        self._logger.debug( "Scheduler.run()" )

#        now = time.mktime( time.localtime() )

#        timer1 = Timer( 'Nederland 1', now + 10, now + 30, {}, Scheduler._callback, self )
#        timer2 = Timer( 'Nederland 1', now + 25, now + 40, {}, Scheduler._callback, self )
#        self._timers.append( timer1 )
#        self._timers.append( timer2 )
#        time.sleep( 15 )
#        timer1.stop()

#        scheduleItem1 = { 'channel': 'Nederland 1', 'startTime': now + 10, 'endTime': now + 30 }
#        scheduleItem2 = { 'channel': 'Nederland 1', 'startTime': now + 25, 'endTime': now + 40 }
#        timer1 = Timer( [ {
#                             'time':              scheduleItem1['startTime'],
#                             'callback':          self._startRecording,
#                             'callbackArguments': scheduleItem1
#                          },
#                          {
#                             'time':              scheduleItem1['endTime'],
#                             'callback':          self._stopRecording,
#                             'callbackArguments': scheduleItem1
#                          } ] )
#        timer2 = Timer( [ {
#                             'time':              scheduleItem2['startTime'],
#                             'callback':          self._startRecording,
#                             'callbackArguments': scheduleItem2
#                          },
#                          {
#                             'time':              scheduleItem2['endTime'],
#                             'callback':          self._stopRecording,
#                             'callbackArguments': scheduleItem2
#                          } ] )
#        self._timers.append( timer1 )
#        self._timers.append( timer2 )
#        time.sleep( 15 )
#        timer1.stop( True )

        # We will want to 'reschedule' when the outside world of this class requests it
        # For testing we just call it once.
        self.reschedule()

        # Keep the thread alive
        while self._running:
            time.sleep( 1.0 )

    def reschedule( self ):
        """
        Find out what programs ('program.Program') to record for each 'schedule.Schedule'

        Process:
        - Sort active schedules by schedule type
        - For each 'schedule' create list of 'newRecordings'
        - For each 'newRecordings' maintain a list of timers.
          - Remove timers that are no longer required --> stop and remove their possible 
            active recording?

        TODO:
        - Handle manual recordings: they do not record a 'program.Program', so no duplicate rules.
          Just make sure the 'recorder.Recorder' will not be too busy at time of recording.
        - Do something with the list of 'recording.Recording's created
        """
        conn = DBConnection()

        schedules     = Schedule.getAllFromDb( conn )
        scheduleTypes = [ Schedule.SCHEDULE_TYPE_ONCE,
                          Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_DAY,
                          Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK,
                          Schedule.SCHEDULE_TYPE_MANUAL_EVERY_DAY,
                          Schedule.SCHEDULE_TYPE_MANUAL_EVERY_WEEKDAY,
                          Schedule.SCHEDULE_TYPE_MANUAL_EVERY_WEEKEND,
                          Schedule.SCHEDULE_TYPE_MANUAL_EVERY_WEEK,
                          Schedule.SCHEDULE_TYPE_ONCE_EVERY_DAY,
                          Schedule.SCHEDULE_TYPE_ONCE_EVERY_WEEK,
                          Schedule.SCHEDULE_TYPE_ANY_TIME ]
        scheduleTypeGroup = {}

        for schedule in schedules:
            if not scheduleTypeGroup.has_key( schedule.type ):
                scheduleTypeGroup[schedule.type] = []
            scheduleTypeGroup[schedule.type].append( schedule )

        newRecordings = []

        # We're going through the schedule list in the order as defined in scheduleTypes
        for scheduleType in scheduleTypes:

            # Are there any recordings with this scheduleType?
            if scheduleTypeGroup.has_key( scheduleType ):

                # Go through schedules in arbitrary order
                for schedule in scheduleTypeGroup[scheduleType]:

                    newRecordings = self._handleSchedule( conn, schedule, newRecordings )

        # Loop through new recordings and create/update timers for them
        # TODO: remove timers that are not needed anymore.
        for recording in newRecordings:
            self._logger.info( "%s", recording.dump() )
            timerFound = False
            with self._lock:
                for timerId in self._timers.keys():
                    timer = self._timers[timerId]
                    if recording.epgProgramId != -1 and \
                       timer["scheduleId"]   == recording.scheduleId and \
                       timer["epgProgramId"] == recording.epgProgramId:
                        self._logger.info( "Updating timer with id=%d" % ( timer["id"] ) )
                        # Update the timer if the startTime is updated
                        if timer["startTime"] != recording.startTime:
                            timer["startTime"] = recording.startTime
                            timer["timer"].changeTimer( 0, datetime.datetime.fromtimestamp( recording.startTime ) )
                        # Update the timer if the endTime is updated
                        if timer["endTime"] != recording.endTime:
                            timer["endTime"] = recording.endTime
                            timer["timer"].changeTimer( 1, datetime.datetime.fromtimestamp( recording.endTime ) )
                        # Make sure we remember the new recording instance, but only if the recording has not started yet
                        if timer["recording"].status == RecordingState.UNKNOWN:
                            timer["recording"] = recording
                        else:
                            # TODO: The recording has started, so update what is relevant
                            self._logger.warning( "We're updating a recording that has started recording, be careful" )
                        timerFound = True
                        break

                if not timerFound:
                    timer = {}
                    if not self._timers.has_key( self._idCounter ):
                        timer["id"]           = self._idCounter
                        timer["scheduleId"]   = recording.scheduleId
                        timer["epgProgramId"] = recording.epgProgramId
                        timer["recording"]    = recording
                        timer["startTime"]    = recording.startTime
                        timer["endTime"]      = recording.endTime
                        timer["recordingId"]  = -1
                        timer["timer"] = Timer( [ { 'time':              datetime.datetime.fromtimestamp( recording.startTime ),
                                                    'callback':          self._startRecording,
                                                    'callbackArguments': timer["id"] },
                                                  { 'time':              datetime.datetime.fromtimestamp( recording.endTime ),
                                                    'callback':          self._stopRecording,
                                                    'callbackArguments': timer["id"] } ] )
                        self._timers[timer["id"]] = timer
                        self._idCounter += 1
                    else:
                        self._logger.critical( "Timer with id=%d already exists!" % ( self._idCounter ) )
            

        """
        No we need to create/update the list of timers. Maybe some of the created recordings 
        were already attached to a timer. Those recordings can be removed again.
        We cannot replace existing recordings with the new one, because the 'Recorder' might
        already have a reference to it (for active recordings). If the recording has change, we
        will need to copy the relevant properties to the existing instance.
        If we want to make it more robust, we should assign a unique ID to which is the same for
        the existing and new recording. This can be difficult, because the properties that make
        a recording unique might change (startTime, endTime, channelId, channelUrlType). For a
        recording that has started, changing startTime, channelId or channelUrlType is useless. 
        """

    def _handleSchedule( self, conn, schedule, newRecordings ):
        """
        Private function that handles one 'schedule.Schedule'

        Process:
        - Get programs that match the 'schedule.title' search criteria
        - For each 'program'
          - Get the (current and old) recordings with same title
          - Remove programs that already have a recording (and rerecord is not requested)
        - For each 'program' in filtered list of programs
          - Check if there is a match timewise (depending on schedule type)
          - Find the best channel and channel url to record from (based on preferences)
          - Check if the recorder will not be busy at this specific time
            - If so, find another channel and channel url and try again
            - Else, create a new 'recording.Recording' and add it to the list
        """

        matchFunction = None

        scheduleType = "<unknown>"
        if schedule.type == Schedule.SCHEDULE_TYPE_ONCE:
            scheduleType  = "SCHEDULE_TYPE_ONCE"
            matchFunction = self._programMatchOnce
        elif schedule.type == Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_DAY:
            scheduleType  = "SCHEDULE_TYPE_TIMESLOT_EVERY_DAY"
            matchFunction = self._programMatchTimeslot
        elif schedule.type == Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK:
            scheduleType  = "SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK"
            matchFunction = self._programMatchTimeslot
        elif schedule.type == Schedule.SCHEDULE_TYPE_ONCE_EVERY_DAY:
            scheduleType  = "SCHEDULE_TYPE_ONCE_EVERY_DAY"
            matchFunction = self._programMatchAnyTime
        elif schedule.type == Schedule.SCHEDULE_TYPE_ONCE_EVERY_WEEK:
            scheduleType  = "SCHEDULE_TYPE_ONCE_EVERY_WEEK"
            matchFunction = self._programMatchAnyTime
        elif schedule.type == Schedule.SCHEDULE_TYPE_ANY_TIME:
            scheduleType  = "SCHEDULE_TYPE_ANY_TIME"
            matchFunction = self._programMatchAnyTime
        elif schedule.type == Schedule.SCHEDULE_TYPE_MANUAL_EVERY_DAY:
            scheduleType = "SCHEDULE_TYPE_MANUAL_EVERY_DAY"
        elif schedule.type == Schedule.SCHEDULE_TYPE_MANUAL_EVERY_WEEKDAY:
            scheduleType = "SCHEDULE_TYPE_MANUAL_EVERY_WEEKDAY"
        elif schedule.type == Schedule.SCHEDULE_TYPE_MANUAL_EVERY_WEEKEND:
            scheduleType = "SCHEDULE_TYPE_MANUAL_EVERY_WEEKEND"
        elif schedule.type == Schedule.SCHEDULE_TYPE_MANUAL_EVERY_WEEK:
            scheduleType = "SCHEDULE_TYPE_MANUAL_EVERY_WEEK"
        else:
            self._logger.critical( "_handleSchedule: Unknown schedule.type=%i" % ( schedule.type ) )
            return newRecordings

        # Get the timeslot of the schedule instance (first occurance of program of interest)
        timeslot = datetime.datetime.fromtimestamp( schedule.startTime )

        self._logger.info( "_handleSchedule: Processing schedule %i - '%s' (%s)" % ( schedule.id, schedule.title, scheduleType ) )
        self._logger.debug( "_handleSchedule: dupMethod=%i, timeslot=%s" % ( schedule.dupMethod, timeslot ) )

        # Get the programs that match this schedule
        # TODO: add 'now' as startTime
        programs = schedule.getPrograms( conn, startTime=time.time() )

        filteredPrograms = programs
        lastRecording    = None
        recordingTitles  = {}

        # Go through list of (possible) program belonging to this schedule
        for program in programs:

            # Title of program may not be unique in list; only filter out duplicates if not already done
            if not recordingTitles.has_key( program.title ):
                recordingTitles[program.title] = True

                # Get recordings with the same title
                # TODO: only get the finished recordings. Active or future recordings will be
                # subject to rescheduling
                recordings    = Recording.getByTitleFromDb( conn, program.title )
                oldRecordings = OldRecording.getByTitleFromDb( conn, program.title )
                filteredPrograms = self._filterOutDuplicates( schedule, filteredPrograms, recordings, oldRecordings=oldRecordings )

                # Find the last recording
                for recording in recordings:
                    if lastRecording and recording.startTime > lastRecording.startTime:
                        lastRecording = recording
                    elif not lastRecording:
                        lastRecording = recording 

        # We've probably reduced the size of the recording candicates 
        programs = filteredPrograms

        # We expect the 'ONCE' type recording to have only matched on program
        if ( schedule.type == Schedule.SCHEDULE_TYPE_ONCE and len( programs ) > 1 ):
            self._logger.warning( "_handleSchedule: More than 1 recording candidate: %i" % ( len( programs ) ) )

        # Now see if there are programs that match the timeslot
        # If we are lucky, all programs will match
        while len( programs ):
            program   = programs.pop( 0 )
            startTime = datetime.datetime.fromtimestamp( program.startTime )

            if matchFunction and matchFunction( schedule, startTime, timeslot, lastRecording ):
                # Yes! We have a match

                newRecording = None 

                # Get all channels that broadcast this program
                channels = Channel.getAllByEpgIdFromDb( conn, program.epgId )
                for channel in channels:
                    # Sort channel urls based on preference for Hd or Unscrambled
                    # Unscrambled is higher priority than Hd 
                    # Default order = sd, hd
                    # TODO: there could be multiple channels with multiple channels: sort total set of urls
                    urls      = channel.urls
                    urlsOrder = []
                    if schedule.preferUnscrambled:
                        if schedule.preferHd and urls.has_key( "hd" ) and not urls["hd"].scrambled:
                            urlsOrder.append( "hd" )
                            if urls.has_key( "sd" ):
                                urlsOrder.append( "sd" )
                        elif urls.has_key( "sd" ) and not urls["sd"].scrambled:
                            urlsOrder.append( "sd" )
                            if urls.has_key( "hd" ):
                                urlsOrder.append( "hd" )
                        elif urls.has_key( "hd" ) and not urls["hd"].scrambled:
                            urlsOrder.append( "hd" )
                            if urls.has_key( "sd" ):
                                urlsOrder.append( "sd" )
                        else:
                            if urls.has_key( "sd "):
                                urlsOrder.append( "sd" )
                            if urls.has_key( "hd "):
                                urlsOrder.append( "hd" )
                    elif urls.has_key( "hd" ) and schedule.preferHd:
                        urlsOrder.append( "hd" )
                        if urls.has_key( "sd" ):
                            urlsOrder.append( "sd" )
                    else:
                        if urls.has_key( "sd" ):
                            urlsOrder.append( "sd" )
                        if urls.has_key( "hd" ):
                            urlsOrder.append( "hd" )

                    for urlType in urlsOrder:
                        newRecording = self._createRecording( schedule, program, channel, urls[urlType] )
                        if self._isRecorderBusyAtTimeframe( newRecordings, schedule, newRecording ):
                            # But oh, it cannot be recorded at that time
                            self._logger.info( "reschedule: Program %i - '%s' starting at %s cannot be recorded because recorder will be busy" % ( program.id, program.title, startTime ) )

                            newRecording = None
                        else:
                            newRecordings.append( newRecording )

                            self._logger.info( "reschedule: Program %i - '%s' starting at %s will be recorded" % ( program.id, program.title, startTime ) )

                            lastRecording = newRecording

                            programs = self._filterOutDuplicates( schedule, programs, newRecordings=newRecordings )

                            # Break from the urls loop
                            break

                    # If newRecording is set, break from channels loop
                    if not newRecording:
                        break
            else:
                self._logger.info( "reschedule: Program %i - '%s' starting at %s does not meet schedule requirements" % ( program.id, program.title, startTime ) )

            if schedule.type == Schedule.SCHEDULE_TYPE_ONCE:
                break

        return newRecordings

    def _programMatchTimeslot( self, schedule, startTime, timeslot, lastRecording ):
        """
        Private function that performs timewise match for timelost based schdules

        A match is found when a program starts at approximately the time set in the schedule
        TODO: The timedelta should become a configuration option
        """
        timeslotOnDayOfProgram = datetime.datetime.combine( startTime.date(), timeslot.time() )
        startDay               = startTime.date()
        lastRecordingStartDay  = datetime.datetime.fromtimestamp( 0 ).date()

        if lastRecording:
            lastRecordingStartDay = datetime.datetime.fromtimestamp( lastRecording.startTime ).date()

        # There is a match when the recording candidate (program) is
        # - On the same day of the week for 'EVERY_WEEK' type
        # - Same time window of the day
        # - Day of program is later than day of last recording
        if ( ( ( schedule.type == Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK and startTime.weekday() == timeslot.weekday() ) or
               ( schedule.type == Schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_DAY ) ) and
             startTime + datetime.timedelta( minutes = 5 ) >= timeslotOnDayOfProgram and
             startTime - datetime.timedelta( minutes = 5 ) <= timeslotOnDayOfProgram and
             startDay > lastRecordingStartDay ):
            return True
        return False

    def _programMatchOnce( self, schedule, startTime, timeslot, lastRecording ):
        """
        Private function that performs exact date/time match for 'record once' schedules

        A match is found when a program starts at exactly the date & time set in the schedule

        TODO: this match will fail when schedule is created before a unforseen change occured
        to the EPG data. Maybe timeslot is better, or should this schedule be explicitly linked
        to this program? 
        """
        if startTime == timeslot:
            return True
        return False

    def _programMatchAnyTime( self, schedule, startTime, timeslot, lastRecording ):
        """
        Private function that performs match for 'record at any time'

        A match is found when
        - 'record at any time', or
        - day of program is same as day of time set in schedule for 'once a week' type and
          the last recording is not on the same day, or
        - first recording of a day for 'once a day' type
        """
        startDay               = startTime.date()
        lastRecordingStartDay  = datetime.datetime.fromtimestamp( 0 ).date()
        if lastRecording:
            lastRecordingStartDay = datetime.datetime.fromtimestamp( lastRecording.startTime ).date()

        startYear, startWeek, startDayOfWeek                                        = startDay.isocalendar()
        lastRecordingStartYear, lastRecordingStartWeek, lastRecordingStartDayOfWeek = lastRecordingStartDay.isocalendar()

        # There is a match when the recording candidate (program) is
        # - Day is later than day of last recording for 'EVERY_DAY' type
        # - Week is later than week of last recording for 'EVERY_WEEK' type (day of week not important)
        # - All for 'ANY_TIME' type
        if ( ( schedule.type == Schedule.SCHEDULE_TYPE_ONCE_EVERY_DAY  and startDay > lastRecordingStartDay ) or
             ( schedule.type == Schedule.SCHEDULE_TYPE_ONCE_EVERY_WEEK and ( ( startYear == lastRecordingStartYear and startWeek > lastRecordingStartWeek ) or
                                                                             ( startYear >  lastRecordingStartYear ) ) ) or
             ( schedule.type == Schedule.SCHEDULE_TYPE_ANY_TIME ) ): 
            return True
        return False

    def _filterOutDuplicates( self, schedule, programs, recordings=[], oldRecordings=[], newRecordings=[] ):
        """
        Private function to filter out duplicates depending on duplicate preferences.
        It will look in list of finished recordings, old recordings (deleted recordings) and newly created recordings
        """
        self._logger.debug( "_filterOutDuplicates()" )

        # list of recordings, oldRecordings, newRecordings can be combined as they are of the same base type (RecordingAbstract)
        recordings = recordings + oldRecordings + newRecordings

        self._logger.debug( "_filterOutDuplicates: len( programs )=%i, len( recordings )=%i" % ( len( programs ), len( recordings ) ) )

        # Check if there is a (old) recording with the same title/subtitle/description in the programs list
        # It is still OK if the programs list contains duplicates: they could become important to fix conflicts
        for program in programs:
            found = False
            self._logger.debug( "_filterOutDuplicates: checking program: title=%s, subtitle=%s, description=%s" % ( program.title, program.subtitle, program.description ) )
            for recording in recordings:
                if ( schedule.dupMethod != Schedule.DUPLICATION_METHOD_NONE and not recording.rerecord and recording.epgProgram and
                     ( ( schedule.dupMethod & Schedule.DUPLICATION_METHOD_TITLE       and program.title       == recording.epgProgram.title )       or not ( schedule.dupMethod & Schedule.DUPLICATION_METHOD_TITLE ) )    and
                     ( ( schedule.dupMethod & Schedule.DUPLICATION_METHOD_SUBTITLE    and program.subtitle    == recording.epgProgram.subtitle )    or not ( schedule.dupMethod & Schedule.DUPLICATION_METHOD_SUBTITLE ) ) and
                     ( ( schedule.dupMethod & Schedule.DUPLICATION_METHOD_DESCRIPTION and program.description == recording.epgProgram.description ) or not ( schedule.dupMethod & Schedule.DUPLICATION_METHOD_DESCRIPTION ) ) ):
                    self._logger.info( "_filterOutDuplicates: found duplicate program: dupMethod=%i, title=%s, subtitle=%s, description=%s" % ( schedule.dupMethod, recording.epgProgram.title, recording.epgProgram.subtitle, recording.epgProgram.description ) )
                    found = True
                    break
            if found:
                programs.remove( program )  

        self._logger.debug( "_filterOutDuplicates: len( programs )=%i" % ( len( programs ) ) )

        return programs

    def _isRecorderBusyAtTimeframe( self, recordings, schedule, newRecording ):
        """
        Private function that checks if the recorder will be too busy to record a specific program
        Since it might be possible that multiple recordings record from a single channel url at a
        given moment, it should count of the number of channels being recorded from

        TODO:
        - number of recorder instances should be configurable
        - next to channelId, also check for channelUrlType
        """
        scheduleStartTime   = schedule.startTime - schedule.startEarly
        scheduleEndTime     = schedule.endTime   + schedule.endLate
        recordingOnChannels = [ newRecording.channelId ]

        for recording in recordings:
            if ( scheduleStartTime <= recording.endTime and
                 scheduleEndTime >= recording.startTime ):
                if recording.channelId not in recordingOnChannels:
                    recordingOnChannels.append( recording.channelId )
            if len( recordingOnChannels ) > 3:
                return True
        return False

    def _createRecording( self, schedule, program, channel, url ):
        """
        program might be None for manual recordings
        program.id refers to EpgProgram. A RecordingProgram will be created when the recording is started
        """
        channelId      = channel.id
        channelName    = channel.name
        channelUrlType = url.channelType
        recording = Recording( -1, schedule.id, program.id, channelId, channelName, channelUrlType, program.startTime, program.endTime, 0, program.title, epgProgram=program )
        return recording

    def _startRecording( self, eventType, timerId ):
        """
        Start a recording
        This function is typically called as callback from Timer

        Current implementation is wrong

        - Lookup recording
        - If applicable, copy EpgProgram to RecordingProgram
        - Set recording state to RecordingState.START_RECORDING
        - Add recording to database
        - Request recorder to start recording
        """
        self._logger.debug( "Scheduler._startRecording" )

        if eventType == Timer.TIME_TRIGGER_EVENT:
            with self._lock:
                if self._timers.has_key( timerId ):
                    timer     = self._timers[timerId]
                    recording = timer["recording"]
                    if recording.status == RecordingState.UNKNOWN:
                        conn       = DBConnection()
                        recorder   = Recorder()
                        channel    = Channel.getFromDb( conn, recording.channelId )
                        if channel.urls.has_key( recording.channelUrlType ):
                            channelUrl       = channel.urls[recording.channelUrlType]
                            recording.changeStatus( None, RecordingState.START_RECORDING )  # Not providing DBConnection, because recording is not in the db yet!
                            self._logger.warning( "_startRecording: Start recording '%s' on channel '%s'" % ( recording.title, recording.channelName ) )
                            timer["recordingId"] = recorder.startRecording( channelUrl, timerId, recording.filename, InputStreamProtocol.HTTP, self._recorderCallback )
                            # Hmm, recordingId is not set, so we couldn't start the recording
                            # Mark recording as unfinished
                            if not timer["recordingId"]:
                                self._logger.critical( "Scheduler._startRecording: recordingId is not set!" )
                                timer.stop()
                                del self._timers[timerId]
                            else:
                                # Convert EpgProgram to RecordingProgram
                                if recording.epgProgramId != -1 and not recording.epgProgram:
                                    recording.epgProgram = EpgProgram.getFromDb( conn, recording.epgProgramId )
                                if recording.epgProgram:
                                    recording.copyEpgProgram()

                                # Store the recording in the database
                                recording.addToDb( conn )
                                self._logger.info( "_startRecording: Recording with id=%d stored in database" % ( recording.id ) )
                                # Now lets keep reference to the id, instead of the object
                                timer["recording"] = recording.id
                        else:
                            self._logger.error( "Channel %s does not have a channelUrl of type %s" % ( channel.name, recording.channelUrlType ) )
                    else:
                        self._logger.error( "_stopRecording: recording with timerId=%d in unexpected state=%d" % ( timerId, recording.status ) )

                    # Unexpected, but if recording is already marked as (un)finished, stop
                    # the timer and remove it from our list
                    if recording.status == RecordingState.RECORDING_FINISHED or \
                       recording.status == RecordingState.RECORDING_UNFINISHED:
                        timer.stop()
                        del self._timers[timerId]
#            item["filename"] = 'temp_%s.ts' % ( item["startTime"] )
#            recorder = Recorder()
#            item["recordingId"] = recorder.startRecording( "123.0.0.321:1234", InputStreamProtocol.HTTP, item["filename"], self._recorderCallback )
#            if not item["recordingId"]:
#                self._logger.critical( "Scheduler._startRecording: recordingId is not set!" )

    def _stopRecording( self, eventType, timerId ):
        """
        Stop a recording
        This function is typically called as callback from Timer

        Current implementation is wrong

        - Lookup recording
        - Request recorder to stop recording
        """
        self._logger.debug( "Scheduler._stopRecording" )
        if eventType == Timer.TIME_TRIGGER_EVENT:
            with self._lock:
                if self._timers.has_key( timerId ):
                    timer     = self._timers[timerId]
                    conn      = DBConnection()
                    self._logger.warning( "_stopRecording: recording id=%d" % ( timer["recording"] ) )
                    recording = Recording.getFromDb( conn, timer["recording"] )
                    if recording:
                        if recording.status == RecordingState.START_RECORDING or \
                           recording.status == RecordingState.RECORDING_STARTED:
                            recorder         = Recorder()
                            recording.changeStatus( conn, RecordingState.STOP_RECORDING )
                            self._logger.warning( "_stopRecording: Stop recording '%s' on channel '%s'" % ( recording.title, recording.channelName ) )
                            recorder.stopRecording( timer["recordingId"], timerId )
                        else:
                            self._logger.error( "_stopRecording: recording with timerId=%d in unexpected state=%d" % ( timerId, recording.status ) )
                    else:
                        self._logger.error( "_stopRecording: recording with timerId=%d and id=%d does not exist in the database" % ( timerId, timer["recording"] ) )
                        recorder.stopRecording( timer["recordingId"], timerId )

#        if eventType == Timer.TIME_TRIGGER_EVENT:
#            recorder = Recorder()
#            recorder.stopRecording( item["recordingId"], item["filename"] )

    def _recorderCallback( self, timerId, recorderState ):
        """
        - Lookup recording
        - Forget about timer and recording
        """
        with self._lock:
            if self._timers.has_key( timerId ):
                conn      = DBConnection()
                timer     = self._timers[timerId]
                self._logger.warning( "_stopRecording: recording id=%d" % ( timer["recording"] ) )
                recording = Recording.getFromDb( conn, timer["recording"] )
                if recording:
                    if recorderState == Recorder.STARTED:
                        if recording.status == RecordingState.START_RECORDING:
                            recording.changeStatus( conn, RecordingState.RECORDING_STARTED )
                            self._logger.warning( "_recorderCallback: Recording '%s' started" % ( recording.title ) )
                        else:
                            self._logger.error( "_recorderCallback: STARTED: recording with timerId=%d in unexpected state=%d" % ( timerId, recording.status ) )

                    elif recorderState == Recorder.FINISHED:
                        if recording.status == RecordingState.STOP_RECORDING:
                            recording.changeStatus( conn, RecordingState.RECORDING_FINISHED )
                            self._logger.warning( "_recorderCallback: Recording '%s' finished" % ( recording.title ) )
                        else:
                            self._logger.error( "_recorderCallback: FINISHED: recording with timerId=%d in unexpected state=%d" % ( timerId, recording.status ) )

                    elif recorderState == Recorder.ABORTED:
                        if recording.status != RecordingState.RECORDING_FINISHED:
                            self._logger.warning( "_recorderCallback: ABORTED: recording with timerId=%d set to UNFINISHED (was %d)" % ( timerId, recording.status ) )
                            recording.changeStatus( conn, RecordingState.RECORDING_UNFINISHED )
                            self._logger.warning( "_recorderCallback: Recording '%s' aborted" % ( recording.title ) )
                        else:
                            self._logger.warning( "_recorderCallback: ABORTED: recording with timerId=%d already finished" % ( timerId ) )

                    if recording.status == RecordingState.RECORDING_FINISHED or \
                       recording.status == RecordingState.RECORDING_UNFINISHED:
                        timer.stop()
                        del self._timers[timerId]
                else:
                    self._logger.error( "_stopRecording: recording with timerId=%d and id=%d does not exist in the database" % ( timerId, timer["recording"] ) )
                    recorder.stopRecording( timer["recordingId"], timerId )
                    timer.stop()
                    del self._timers[timerId]
            else:
                self._logger.error( "_recorderCallback: recording with timerId=%d not found" % ( timerId ) )

