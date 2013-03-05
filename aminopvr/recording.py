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
from aminopvr.epg import RecordingProgram
import copy
import epg
import logging
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
        self._id              = id
        self._scheduleId      = scheduleId
        self._epgProgramId    = epgProgramId
        self._channelId       = channelId
        self._channelName     = channelName
        self._channelUrlType  = channelUrlType
        self._startTime       = startTime
        self._endTime         = endTime
        self._length          = length
        self._title           = title
        self._filename        = filename
        self._fileSize        = fileSize
        self._streamArguments = streamArguments
        self._type            = type
        self._scrambled       = scrambled
        self._marker          = marker
        self._status          = status
        self._rerecord        = rerecord
        self._epgProgram      = epgProgram

#        if self._filename = "":
#            self._filename = self._createFilename()

    def __hash__( self ):
        return ( hash( self._scheduleId + self.epgProgramId + self._channelId ) +
                 hash( self._startTime + self._endTime + self._length ) +
                 hash( self._channelName + self._title + self._filename + self._streamArguments ) +
                 hash( self._fileSize + self._type + self._scrambled + self._marker ) +
                 hash( self._status + self._rerecord ) )

    def __eq__( self, other ):
        # Not comparng _id as it might not be set at comparison time.
        # For insert/update descision it is not relevant
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
    def getAllFromDb( cls, conn ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recordings = []
        if conn:
            rows = conn.execute( "SELECT * FROM %s ORDER BY start_time ASC" % ( cls._tableName ) ).fetchall()
            for row in rows:
                recording = cls._createRecordingFromDbDict( conn, row )
                recordings.append( recording )

        return recordings

    @classmethod
    def getAllByScheduleIdFromDb( cls, conn, scheduleId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recordings = []
        if conn:
            rows = conn.execute( "SELECT * FROM %s WHERE schedule_id = ? ORDER BY start_time ASC" % ( cls._tableName ), ( scheduleId, ) ).fetchall()
            for row in rows:
                recording = cls._createRecordingFromDbDict( conn, row )
                recordings.append( recording )

        return recordings

    @classmethod
    def getByTitleFromDb( cls, conn, title ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recordings = []
        title      = '%' + title + '%'
        if conn:
            rows = conn.execute( "SELECT * FROM %s WHERE title LIKE ? ORDER BY start_time ASC" % ( cls._tableName ), ( title, ) ).fetchall()
            for row in rows:
                recording = cls._createRecordingFromDbDict( conn, row )
                recordings.append( recording )

        return recordings

    @classmethod
    def getAllUnfinishedFromDb( cls, conn ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recordings = []
        if conn:
            rows = conn.execute( "SELECT * FROM %s WHERE status > ? AND status < ? ORDER BY start_time ASC" % ( cls._tableName ), ( RecordingState.STATUS_UNKNOWN, RecordingState.RECORDING_FINISHED ) ).fetchall()
            for row in rows:
                recording = cls._createRecordingFromDbDict( conn, row )
                recordings.append( recording )

        return recordings

    @classmethod
    def getFromDb( cls, conn, id ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        recording = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE id = ?" % ( cls._tableName ), ( id, ) ).fetchone()
            recording = cls._createRecordingFromDbDict( conn, row )

        return recording

    @classmethod
    def _createRecordingFromDbDict( cls, conn, data ):
        recording = None
        if data:
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

    def dump( self ):
        return ( "%s - %i: %i, %i, %i, %i, %i, %s, %s, %i" % ( self._tableName, self._id, self._scheduleId, self._epgProgramId, self._startTime, self._endTime, self._length, repr( self._title ), repr( self._filename ), self._status ) )

class Recording( RecordingAbstract ):
    _tableName = "recordings"

    _logger    = logging.getLogger( 'aminopvr.Recording' )

    def changeStatus( self, conn, status ):
        if conn and self._id == -1:
            self._logger.error( "changeStatus: cannot change recording status; recording not in database yet" )
            return
        self._status = status
        if conn:
            # TODO: set fileSize and length when status == RECORDING_STATUS_RECORDING_FINISHED
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
