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
from aminopvr.database.channel import Channel, ChannelAbstract
from aminopvr.database.cache import Cache
from aminopvr.database.epg import RecordingProgram, ProgramAbstract
from aminopvr.tools import printTraceback
import copy
import datetime
import logging
import os
import sys

class RecordingState( object ):
    UNKNOWN              = 0
    START_RECORDING      = 1
    RECORDING_STARTED    = 2
    STOP_RECORDING       = 3
    RECORDING_FINISHED   = 4
    RECORDING_UNFINISHED = 5

class RecordingAbstract( object ):

    _tableName       = None

    def __init__( self, id=-1 ):    # @ReservedAssignment
        self._id                = int( id )
        self._scheduleId        = -1
        self._epgProgramId      = -1
        self._channelId         = -1
        self._channelName       = "Channel 1"
        self._channelUrlType    = ""
        self._startTime         = 0
        self._endTime           = 0
        self._length            = 0
        self._title             = "Title"
        self._filename          = ""
        self._fileSize          = 0
        self._streamArguments   = ""
        self._type              = "sd"
        self._scrambled         = False
        self._marker            = 0
        self._status            = RecordingState.UNKNOWN
        self._rerecord          = False
        self._channel           = None
        self._epgProgram        = None

    def __hash__( self ):
        return ( hash( hash( self._scheduleId ) +
                       hash( self._epgProgramId ) +
                       hash( self._channelId ) +
                       hash( self._channelName ) +
                       hash( self._channelUrlType ) +
                       hash( self._startTime ) +
                       hash( self._endTime ) +
                       hash( self._length ) +
                       hash( self._title ) +
                       hash( self._filename ) +
                       hash( self._fileSize ) +
                       hash( self._streamArguments ) +
                       hash( self._type ) +
                       hash( self._scrambled ) +
                       hash( self._marker ) +
                       hash( self._status ) +
                       hash( self._rerecord ) ) )

    def __eq__( self, other ):
        # Not comparing _id as it might not be set at comparison time.
        # For insert/update decision it is not relevant
        if not other:
            return False
        assert isinstance( other, RecordingAbstract ), "Other object not instance of class RecordingAbstract: %r" % ( other )
        return ( self._scheduleId       == other._scheduleId        and
                 self._epgProgramId     == other._epgProgramId      and
                 self._channelId        == other._channelId         and
                 self._channelName      == other._channelName       and
                 self._channelUrlType   == other._channelUrlType    and
                 self._startTime        == other._startTime         and
                 self._endTime          == other._endTime           and
                 self._length           == other._length            and
                 self._title            == other._title             and
                 self._filename         == other._filename          and
                 self._fileSize         == other._fileSize          and
                 self._streamArguments  == other._streamArguments   and
                 self._type             == other._type              and
                 self._scrambled        == other._scrambled         and
                 self._marker           == other._marker            and
                 self._status           == other._status            and
                 self._rerecord         == other._rerecord )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @classmethod
    def copy( cls, recording ):
        if isinstance( recording, RecordingAbstract ):
            recording = copy.copy( recording )
            recording.__class__ = cls
            recording._id       = -1
            return recording
        return None

    @property
    def id( self ):
        return self._id

    @property
    def scheduleId( self ):
        return self._scheduleId

    @scheduleId.setter
    def scheduleId( self, scheduleId ):
        self._scheduleId = int( scheduleId )

    @property
    def epgProgramId( self ):
        return self._epgProgramId

    @epgProgramId.setter
    def epgProgramId( self, epgProgramId ):
        self._epgProgramId = int( epgProgramId )

    @property
    def epgProgram( self ):
        return self._epgProgram

    @epgProgram.setter
    def epgProgram( self, epgProgram ):
        self._epgProgram = epgProgram
        if epgProgram:
            if not isinstance( epgProgram, ProgramAbstract ):
                assert False, "Recording.epgProgram: epgProgram not a ProgramAbstract instance: %r" % ( epgProgram )
                self._epgProgram   = None
                self._epgProgramId = -1
            else:
                self._epgProgramId = epgProgram.id

    @property
    def channelId( self ):
        return self._channelId

    @channelId.setter
    def channelId( self, channelId ):
        self._channelId = int( channelId )

    @property
    def channelName( self ):
        return self._channelName

    @channelName.setter
    def channelName( self, channelName ):
        self._channelName = unicode( channelName )

    @property
    def channelUrlType( self ):
        return self._channelUrlType

    @channelUrlType.setter
    def channelUrlType( self, channelUrlType ):
        self._channelUrlType = unicode( channelUrlType )

    @property
    def channel( self ):
        return self._channel

    @channel.setter
    def channel( self, channel ):
        self._channel = channel
        if channel:
            if not isinstance( channel, ChannelAbstract ):
                assert False, "Recording.channel: channel not a ChannelAbstract instance: %r" % ( channel )
                self._channel   = None
                self._channelId = -1;
            else:
                self._channelId = channel.id

    @property
    def startTime( self ):
        return self._startTime

    @startTime.setter
    def startTime( self, startTime ):
        self._startTime = int( startTime )

    @property
    def endTime( self ):
        return self._endTime

    @endTime.setter
    def endTime( self, endTime ):
        self._endTime = int( endTime )

    @property
    def length( self ):
        return self._length

    @length.setter
    def length( self, length ):
        self._length = int( length )

    @property
    def title( self ):
        return self._title

    @title.setter
    def title( self, title ):
        self._title = unicode( title )

    @property
    def filename( self ):
        return self._filename

    @filename.setter
    def filename( self, filename ):
        self._filename = unicode( filename )

    @property
    def fileSize( self ):
        return self._fileSize

    @fileSize.setter
    def fileSize( self, fileSize ):
        self._fileSize = int( fileSize )

    @property
    def streamArguments( self ):
        return self._streamArguments

    @streamArguments.setter
    def streamArguments( self, streamArguments ):
        self._streamArguments = unicode( streamArguments )

    @property
    def type( self ):
        return self._type

    @type.setter
    def type( self, type ): # @ReservedAssignment
        self._type = unicode( type )

    @property
    def scrambled( self ):
        return self._scrambled

    @scrambled.setter
    def scrambled( self, scrambled ):
        self._scrambled = int( scrambled )

    @property
    def marker( self ):
        return self._marker

    @marker.setter
    def marker( self, marker ):
        self._marker = int( marker )

    @property
    def status( self ):
        return self._status

    @status.setter
    def status( self, status ):
        self._status = int( status )

    @property
    def rerecord( self ):
        return self._rerecord

    @rerecord.setter
    def rerecord( self, rerecord ):
        self._rerecord = int( rerecord )

    @classmethod
    def getAllFromDb( cls, conn, finishedOnly=True, offset=None, count=None, sort=None ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recordings = []
        if conn:
            limit = ""
            where = ""

            if offset != None and count != None:
                limit = " LIMIT %d, %d" % ( offset, count )

            if sort != None:
                sort = "%s ASC" % ( sort )
            else:
                sort = "start_time DESC"

            if finishedOnly:
                where = " WHERE status = %d" % ( RecordingState.RECORDING_FINISHED )

            rows = conn.execute( "SELECT * FROM %s%s ORDER BY %s%s" % ( cls._tableName, where, sort, limit ) )
            for row in rows:
                recording = cls._createRecordingFromDbDict( conn, row )
                recordings.append( recording )

        return recordings

    @classmethod
    def getNumRecordingsFromDb( cls, conn ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        numRecordings = 0
        if conn:
            numRecordings = conn.execute( "SELECT COUNT(*) AS num_recordings FROM %s" % ( cls._tableName ) )[0]["num_recordings"]
        return numRecordings

    @classmethod
    def getAllByScheduleIdFromDb( cls, conn, scheduleId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recordings = []
        if conn:
            rows = conn.execute( "SELECT * FROM %s WHERE schedule_id = ? ORDER BY start_time ASC" % ( cls._tableName ), ( scheduleId, ) )
            for row in rows:
                recording = cls._createRecordingFromDbDict( conn, row )
                recordings.append( recording )

        return recordings

    @classmethod
    def getByTitleFromDb( cls, conn, title, finishedOnly=False ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recordings = []
        title      = '%' + title + '%'
        if conn:
            rows = []
            if finishedOnly:
                rows = conn.execute( "SELECT * FROM %s WHERE status=? AND title LIKE ? ORDER BY start_time ASC" % ( cls._tableName ), ( RecordingState.RECORDING_FINISHED, title ) )
            else:
                rows = conn.execute( "SELECT * FROM %s WHERE title LIKE ? ORDER BY start_time ASC" % ( cls._tableName ), ( title, ) )
            for row in rows:
                recording = cls._createRecordingFromDbDict( conn, row )
                recordings.append( recording )

        return recordings

    @classmethod
    def getByEpgProgramIdFromDb( cls, conn, epgProgramId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recording = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE epg_program_id = ?" % ( cls._tableName ), ( epgProgramId, ) )
            if row:
                recording = cls._createRecordingFromDbDict( conn, row[0] )

        return recording

    @classmethod
    def getByScheduleIdChannelIdAndTimeFromDb( cls, conn, scheduleId, channelId, startTime, endTime ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recording = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE schedule_id = ? AND channel_id = ? AND start_time = ? AND end_time = ?" % ( cls._tableName ), ( scheduleId, channelId, startTime, endTime ) )
            if row:
                recording = cls._createRecordingFromDbDict( conn, row[0] )

        return recording

    @classmethod
    def getAllUnfinishedFromDb( cls, conn ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recordings = []
        if conn:
            rows = conn.execute( "SELECT * FROM %s WHERE status > ? AND status < ? ORDER BY start_time ASC" % ( cls._tableName ), ( RecordingState.UNKNOWN, RecordingState.RECORDING_FINISHED ) )
            for row in rows:
                recording = cls._createRecordingFromDbDict( conn, row )
                recordings.append( recording )

        return recordings

    @classmethod
    def getFromDb( cls, conn, id ):  # @ReservedAssignment
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recording = Cache().get( cls._tableName, id )
        if not recording and conn:
            row = conn.execute( "SELECT * FROM %s WHERE id = ?" % ( cls._tableName ), ( id, ) )
            if row:
                recording = cls._createRecordingFromDbDict( conn, row[0] )

        return recording

    @classmethod
    def _createRecordingFromDbDict( cls, conn, data ):
        recording = None
        if data:
            try:
                recording                   = cls( data["id"] )
                recording.scheduleId        = data["schedule_id"]
                recording.epgProgramId      = data["epg_program_id"]
                recording.channelId         = data["channel_id"]
                recording.channelName       = data["channel_name"]
                recording.channelUrlType    = data["channel_url_type"]
                recording.startTime         = data["start_time"]
                recording.endTime           = data["end_time"]
                recording.length            = data["length"]
                recording.title             = data["title"]
                recording.filename          = data["filename"]
                recording.fileSize          = data["file_size"]
                recording.streamArguments   = data["stream_arguments"]
                recording.type              = data["type"]
                recording.scrambled         = data["scrambled"]
                recording.marker            = data["marker"]
                recording.status            = data["status"]
                recording.rerecord          = data["rerecord"]

                if recording.epgProgramId != -1:
                    recording.epgProgram = RecordingProgram.getFromDb( conn, recording.epgProgramId )
                    if not recording.epgProgram:
                        recording.epgProgramId = -1

                if recording.channelId != -1:
                    recording.channel = Channel.getFromDb( conn, recording.channelId )
                    if not recording.channel:
                        recording.channelId = -1

                Cache().cache( cls._tableName, recording.id, recording )
            except:
                cls._logger.error( "_createRecordingFromDbDict: unexpected error: %s" % ( sys.exc_info()[0] ) )
                printTraceback()

        return recording

    def addToDb( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
#            recording = None
# This shouldn't be necessary
#             if self._id != -1:
#                 recording = self.getFromDb( conn, self._id )
#                 if not recording:
#                     self._id = -1

            if self._id != -1:
                conn.execute( """
                                 UPDATE
                                     %s
                                 SET
                                     schedule_id=?,
                                     epg_program_id=?,
                                     channel_id=?,
                                     channel_name=?,
                                     channel_url_type=?,
                                     start_time=?,
                                     end_time=?,
                                     length=?,
                                     title=?,
                                     filename=?,
                                     file_size=?,
                                     stream_arguments=?,
                                     type=?,
                                     scrambled=?,
                                     marker=?,
                                     status=?,
                                     rerecord=?
                                 WHERE
                                     id=?
                              """ % ( self._tableName ),
                              ( self._scheduleId,
                                self._epgProgramId,
                                self._channelId,
                                self._channelName,
                                self._channelUrlType,
                                self._startTime,
                                self._endTime,
                                self._length,
                                self._title,
                                self._filename,
                                self._fileSize,
                                self._streamArguments,
                                self._type,
                                self._scrambled,
                                self._marker,
                                self._status,
                                self._rerecord,
                                self._id ) )
            else:
                if self._filename == "":
                    self._filename = self._generateFilename( conn )

                if self._epgProgramId == -1 and self._epgProgram:
                    assert isinstance( self._epgProgram, RecordingProgram ), "self._epgProgram not of type RecordingProgram: %r" % ( self._epgProgram ) 
                    self._epgProgram.addToDb( conn )
                    self._epgProgramId = self._epgProgram.id

                recordingId = conn.insert( """
                                              INSERT INTO
                                                  %s (schedule_id,
                                                      epg_program_id,
                                                      channel_id,
                                                      channel_name,
                                                      channel_url_type,
                                                      start_time,
                                                      end_time,
                                                      length,
                                                      title,
                                                      filename,
                                                      file_size,
                                                      stream_arguments,
                                                      type,
                                                      scrambled,
                                                      marker,
                                                      status,
                                                      rerecord)
                                              VALUES
                                                  (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                           """ % ( self._tableName ),
                                           ( self._scheduleId,
                                             self._epgProgramId,
                                             self._channelId,
                                             self._channelName,
                                             self._channelUrlType,
                                             self._startTime,
                                             self._endTime,
                                             self._length,
                                             self._title,
                                             self._filename,
                                             self._fileSize,
                                             self._streamArguments,
                                             self._type,
                                             self._scrambled,
                                             self._marker,
                                             self._status,
                                             self._rerecord ) )
                if recordingId:
                    self._id = recordingId

            Cache().cache( self._tableName, self.id, self )

    def toDict( self ):
        recordingDict = { "id":           self.id,
                          "schedule_id":  self.scheduleId,
                          "start_time":   self.startTime,
                          "end_time":     self.endTime,
                          "length":       self.length,
                          "title":        self.title,
                          "url":          "/recordings/%d" % ( self.id ),
                          "filename":     self.filename,
                          "file_size":    self.fileSize / 1024 / 1024,
                          "scrambled":    self.scrambled,
                          "marker":       self.marker,
                          "status":       self.status }

        if self.epgProgram:
            recordingDict["epg_program_id"] = self.epgProgramId
            recordingDict["epg_program"]    = self.epgProgram.toDict()
        else:
            recordingDict["epg_program_id"] = -1

        if self.channel:
            recordingDict["channel_id"]     = self.channelId
            recordingDict["channel_name"]   = self.channel.name
            recordingDict["channel"]        = self.channel.toDict()
        else:
            recordingDict["channel_id"]     = -1
            recordingDict["channel_name"]   = self.channelName

        return recordingDict

    def _generateFilename( self, conn ):
        channel  = Channel.getFromDb( conn, self._channelId )
        filename = "%04d_%s.ts" % ( channel.number, datetime.datetime.fromtimestamp( self._startTime ).strftime( "%Y%m%d%H%M%S" ) )
        return filename

    def dump( self ):
        return ( "%s - %i: %i, %i, %i, %i, %i, %s, %s, %i" % ( self._tableName, self._id, self._scheduleId, self._epgProgramId, self._startTime, self._endTime, self._length, repr( self._title ), repr( self._filename ), self._status ) )

class Recording( RecordingAbstract ):
    _tableName = "recordings"

    _logger    = logging.getLogger( 'aminopvr.Recording' )

    def deleteFromDb( self, conn, rerecord=False ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
            self._logger.warning( "Remove recording id=%d (%s recorded at %s from %s; rerecord=%s)" % ( self._id, self._title, datetime.datetime.fromtimestamp( self._startTime ), self._channelName, rerecord ) )

            # Re-record prevention only makes sense when recording is linked to an actual program
            if self._epgProgramId != -1:
                if not rerecord:
                    self._logger.info( "Creating copy of recording to prevent re-recording of this program" )
                    oldRecording     = OldRecording.copy( self )
                    oldRecording.addToDb( conn )
                else:
                    # remove RecordingProgram
                    self._logger.info( "Remove recording program to allow re-recording of this program" )
                    recordingProgram = RecordingProgram.getFromDb( conn, self._epgProgramId )
                    if recordingProgram:
                        recordingProgram.deleteFromDb( conn )
                    else:
                        self._logger.error( "Recording program with epgProgramId=%d does not exist!" % ( self._epgProgramId ) )

            generalConfig     = GeneralConfig( Config() )
            recordingFilename = os.path.abspath( os.path.join( generalConfig.recordingsPath, self._filename ) )
            if os.path.islink( recordingFilename ) or os.path.isfile( recordingFilename ):
                os.unlink( recordingFilename )

            conn.execute( "DELETE FROM %s WHERE id=?" % ( self._tableName ), ( self._id, ) )

            Cache().purge( self._tableName, self.id )

    def changeStatus( self, conn, status ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if self._id == -1:
            self._logger.error( "changeStatus: cannot change recording status; recording not in database yet" )
            return
        if self._status != status:
            self._status = status
            if conn:
                if status == RecordingState.RECORDING_FINISHED or status == RecordingState.RECORDING_UNFINISHED:
                    generalConfig     = GeneralConfig( Config() )
                    recordingFilename = os.path.abspath( os.path.join( generalConfig.recordingsPath, self._filename ) )
                    if os.path.exists( recordingFilename ):
                        self._fileSize = os.stat( recordingFilename ).st_size;
                    self._logger.warning( "changeStatus: recording (un)finished; status=%d, fileSize=%d" % ( self._status, self._fileSize ) )
                    conn.execute( "UPDATE %s SET status=?, file_size=? WHERE id=?" % ( self._tableName ), ( status, self._fileSize, self._id ) )
                else:
                    conn.execute( "UPDATE %s SET status=? WHERE id=?" % ( self._tableName ), ( status, self._id ) )

            Cache().purge( self._tableName, self.id )
        else:
            self._logger.warning( "changeStatus: status of recording with id=%d didn't change: %d == %d" % ( self._id, self._status, status ) )

    def copyEpgProgram( self ):
        if self._epgProgram:
            self._epgProgram   = RecordingProgram.copy( self._epgProgram )
            self._epgProgramId = self._epgProgram.id


class OldRecording( RecordingAbstract ):
    _tableName = "old_recordings"

    _logger    = logging.getLogger( 'aminopvr.OldRecording' )

    def deleteFromDb( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
            if self._epgProgramId != -1:
                # remove RecordingProgram
                recordingProgram = RecordingProgram.getFromDb( conn, self._epgProgramId )
                recordingProgram.deleteFromDb( conn )

            conn.execute( "DELETE FROM %s WHERE id = ?" % ( self._tableName ), ( self._id, ) )

            Cache().purge( self._tableName, self.id )

def main():
    sys.stderr.write( "main()\n" );

# allow this to be a module
if __name__ == '__main__':
    main()
