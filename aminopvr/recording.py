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
from aminopvr.config import GeneralConfig, Config
from aminopvr.epg import RecordingProgram
import copy
import datetime
import epg
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

    def __init__( self, id, scheduleId, epgProgramId, channelId, channelName, channelUrlType, startTime, endTime, length, title, filename="", fileSize=0, streamArguments="", marker=0, type="sd", scrambled=0, status=RecordingState.UNKNOWN, rerecord=False, epgProgram=None ):
        self._id              = int( id )
        self._scheduleId      = int( scheduleId )
        self._epgProgramId    = int( epgProgramId )
        self._channelId       = int( channelId )
        self._channelName     = unicode( channelName )
        self._channelUrlType  = unicode( channelUrlType )
        self._startTime       = int( startTime )
        self._endTime         = int( endTime )
        self._length          = int( length )
        self._title           = unicode( title )
        self._filename        = unicode( filename )
        self._fileSize        = int( fileSize )
        self._streamArguments = unicode( streamArguments )
        self._type            = unicode( type )
        self._scrambled       = int( scrambled )
        self._marker          = int( marker )
        self._status          = int( status )
        self._rerecord        = int( rerecord )
        self._epgProgram      = epgProgram

#        if self._filename = "":
#            self._filename = self._createFilename()

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
        # Not comparng _id as it might not be set at comparison time.
        # For insert/update descision it is not relevant
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
            return recording
        return None

    @property
    def id( self ):
        return self._id

    @property
    def scheduleId( self ):
        return self._scheduleId

    @property
    def epgProgramId( self ):
        return self._epgProgramId

    @epgProgramId.setter
    def epgProgramId( self, epgProgramId ):
        self._epgProgramId = epgProgramId

    @property
    def epgProgram( self ):
        return self._epgProgram

    @epgProgram.setter
    def epgProgram( self, epgProgram ):
        self._epgProgram = epgProgram
        if epgProgram:
            self._epgProgramId = epgProgram.id

    @property
    def channelId( self ):
        return self._channelId

    @property
    def channelName( self ):
        return self._channelName

    @property
    def channelUrlType( self ):
        return self._channelUrlType

    @property
    def startTime( self ):
        return self._startTime

    @property
    def endTime( self ):
        return self._endTime

    @property
    def length( self ):
        return self._length

    @property
    def title( self ):
        return self._title

    @property
    def filename( self ):
        return self._filename

    @property
    def fileSize( self ):
        return self._fileSize

    @property
    def streamArguments( self ):
        return self._streamArguments

    @property
    def type( self ):
        return self._type

    @property
    def scrambled( self ):
        return self._scrambled

    @property
    def marker( self ):
        return self._marker

    @marker.setter
    def marker( self, marker ):
        self._marker = marker

    @property
    def status( self ):
        return self._status

    @property
    def rerecord( self ):
        return self._rerecord

    @rerecord.setter
    def rerecord( self, rerecord ):
        self._rerecord = rerecord

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
    def getAllUnfinishedFromDb( cls, conn ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recordings = []
        if conn:
            rows = conn.execute( "SELECT * FROM %s WHERE status > ? AND status < ? ORDER BY start_time ASC" % ( cls._tableName ), ( RecordingState.STATUS_UNKNOWN, RecordingState.RECORDING_FINISHED ) )
            for row in rows:
                recording = cls._createRecordingFromDbDict( conn, row )
                recordings.append( recording )

        return recordings

    @classmethod
    def getFromDb( cls, conn, id ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recording = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE id = ?" % ( cls._tableName ), ( id, ) )
            if row:
                recording = cls._createRecordingFromDbDict( conn, row[0] )

        return recording

    @classmethod
    def _createRecordingFromDbDict( cls, conn, data ):
        recording = None
        if data:
            try:
                recording = cls( id              = data["id"],
                                 scheduleId      = data["schedule_id"],
                                 epgProgramId    = data["epg_program_id"],
                                 channelId       = data["channel_id"],
                                 channelName     = data["channel_name"],
                                 channelUrlType  = data["channel_url_type"],
                                 startTime       = data["start_time"],
                                 endTime         = data["end_time"],
                                 length          = data["length"],
                                 title           = data["title"],
                                 filename        = data["filename"],
                                 fileSize        = data["file_size"],
                                 streamArguments = data["stream_arguments"],
                                 marker          = data["marker"],
                                 type            = data["type"],
                                 scrambled       = data["scrambled"],
                                 status          = data["status"],
                                 rerecord        = False ) # TODO data["rerecord"]
                if recording._epgProgramId != -1:
                    recording._epgProgram = epg.RecordingProgram.getFromDb( conn, recording._epgProgramId )
                    if not recording._epgProgram:
                        recording._epgProgramId = -1
            except:
                cls._logger.error( "_createRecordingFromDbDict: unexpected error: %s" % ( sys.exc_info()[0] ) )

        return recording

    def deleteFromDB( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
            conn.execute( "DELETE FROM %s WHERE id = ?" % ( self._tableName ), ( self._id, ) )
            if self._epgProgramId == -1 and self._epgProgram:
                self._epgProgram.locked = 0
                self._epgProgram.addToDb( conn )

    def addToDb( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
            recording = None
            if self._id != -1:
                recording = self.getFromDb( conn, self._id )
                if not recording:
                    self._id = -1

            if self._id != -1:
                if recording and self != recording:
                    conn.execute( """
                                     UPDATE
                                         %s
                                     SET
                                         schedule_id=?,
                                         epg_program_id=?,
                                         channel_id=?
                                         channel_name=?
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
                                         id=%s
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

                id = conn.insert( """
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
                if id:
                    self._id = id

    def toDict( self ):
        return { "id":           self.id,
                 "start_time":   self.startTime,
                 "end_time":     self.endTime,
                 "title":        self.epgProgram.title,
                 "subtitle":     self.epgProgram.subtitle,
                 "description":  self.epgProgram.description,
                 "channel_id":   self.channelId,
                 "channel_name": self.channelName,
                 "url":          "/aminopvr/recordings/%d" % ( self.id ),
                 "marker":       self.marker }

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
        if conn:
            if not rerecord:
                self._logger.warning( "Creating copy of recording to prevent re-recording of this program" )
                oldRecording = OldRecording.copy( self )
                oldRecording.addToDb( conn )
            else:
                # remove RecordingProgram
                recordingProgram = RecordingProgram.getFromDb( conn, self._epgProgramId )
                recordingProgram.deleteFromDb( conn )

            generalConfig     = GeneralConfig( Config() )
            recordingFilename = os.path.abspath( os.path.join( generalConfig.recordingsPath, self._filename ) )
            if os.path.exists( recordingFilename ):
                os.unlink( recordingFilename )

            conn.execute( "DELETE FROM recordings WHERE id=?", ( self._id, ) )

    def changeStatus( self, conn, status ):
        if self._id == -1:
            self._logger.error( "changeStatus: cannot change recording status; recording not in database yet" )
            return
        if self._status != status:
            self._status = status
            if conn:
                if status == RecordingState.RECORDING_FINISHED or status == RecordingState.RECORDING_UNFINISHED:
                    generalConfig     = GeneralConfig( Config() )
                    recordingFilename = os.path.abspath( os.path.join( generalConfig.recordingsPath, self._filename ) )
                    recordingFileSize = 0
                    if os.path.exists( recordingFilename ):
                        recordingFileSize = os.stat( recordingFilename ).st_size;
                    conn.execute( "UPDATE recordings SET status=?, file_size=? WHERE id=?", ( status, recordingFileSize, self._id ) )
                else:
                    conn.execute( "UPDATE recordings SET status=? WHERE id=?", ( status, self._id ) )

    def copyEpgProgram( self ):
        if self._epgProgram:
            self._epgProgram   = RecordingProgram.copy( self._epgProgram )
            self._epgProgramId = self._epgProgram.id


class OldRecording( RecordingAbstract ):
    _tableName = "old_recordings"

    _logger    = logging.getLogger( 'aminopvr.OldRecording' )

def main():
    sys.stderr.write( "main()\n" );
    recording = Recording( -1, -1, -1, -1, "Chan 1", 0, 100, 100, "Rec 1" )
    sys.stderr.write( "%s\n" % ( recording.dump() ) )

    oldRecording = OldRecording.copy( recording )
    sys.stderr.write( "%s\n" % ( oldRecording.dump() ) )

# allow this to be a module
if __name__ == '__main__':
    main()
