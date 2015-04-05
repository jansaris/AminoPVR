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
# from aminopvr.input_stream import InputStreamAbstract
# from aminopvr.resource_monitor import Watchdog
from aminopvr.tools import Singleton, printTraceback
from aminopvr.virtual_tuner import VirtualTuner
from Queue import Queue
import logging
import stat
import os
import threading
# import uuid

# BUFFER_SIZE             = 40 * 188
# WATCHDOG_KICK_PERIOD    = 5


class ActiveRecording( object ):

    _logger = logging.getLogger( "aminopvr.ActiveRecording" )

    STARTED  = 1
    ABORTED  = 2
    FINISHED = 3

    def __init__( self, id, url, protocol, outputFile, callback ):
        """
        Initialize 'ActiveRecording' instance.

        @param id:                  recording identifier
        @param url:                 instance of ChannelUrl class
        @param protocol:            protocol to be used to get the input stream (e.g. multicast, http)
        @param outputFile:          filename of output file
        @param callback:            status callback
        """
        self._logger.debug( "ActiveRecording.__init__( id=%r, url=%s, protocol=%s, outputFile=%s )" % ( id, url, protocol, outputFile ) )

        self._id            = id
        self._url           = url
        self._protocol      = protocol
        self._outputFile    = outputFile
        self._callback      = callback
        self._tuner         = VirtualTuner.getTuner( url, protocol )
        self._output        = None

    def start( self ):
        if self._tuner:
            self._tuner.addListener( self._id, self._dataCallback )
            try:
                fd = os.open( self._outputFile, os.O_WRONLY | os.O_CREAT, 0644 )
                os.chmod( self._outputFile, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH )
                self._output = os.fdopen( fd, "wb" )
                self._notifyListener( ActiveRecording.STARTED )
            except:
                self._logger.error( "ActiveRecording.__init__: error while creating recording %s" % ( self._outputFile ) )
                printTraceback()
                self._notifyListener( ActiveRecording.ABORTED )
        else:
            self._logger.error( "ActiveRecording.__init__: Unable to get tuner" )
            self._notifyListener( ActiveRecording.ABORTED )

    def stop( self, abort=False ):
        if self._tuner:
            self._tuner.removeListener( self._id )
            self._tuner = None
            if self._output:
                self._output.close()
                self._output = None
            if abort:
                self._notifyListener( ActiveRecording.ABORTED )
            else:
                self._notifyListener( ActiveRecording.FINISHED )

    def _dataCallback( self, id_, data ):
        if data:
            try:
                self._output.write( data )
            except:
                self._logger.error( "ActiveRecording._dataCallback: error while writing to recording %s" % ( self._outputFile ) )
                printTraceback()
                self.stop( True )
        else:
            self._logger.warning( "ActiveRecording._dataCallback: didn't receive data" )
            self.stop( True )

    def _notifyListener( self, result ):
        if self._callback:
            self._callback( self._id, result )

class _RecorderQueueItem( object ):
    STOP_RECORDER       = 1
    STOP_ALL_RECORDINGS = 2
    START_RECORDING     = 3
    STOP_RECORDING      = 4
    ABORT_RECORDING     = 5
    RECORDING_STARTED   = 6
    RECORDING_STOPPED   = 7
    RECORDING_ABORTED   = 8
    def __init__( self, id_, data=None ):
        self.id   = id_
        self.data = data

class Recorder( threading.Thread ):
    """
    Singleton class that is the arbiter for all (active) recordings.

    New recordings are added through startRecording
    Recordings can be stopped through stopRecording
    """
    __metaclass__ = Singleton

    _recordings = {}
    _queue      = Queue()
    _logger     = logging.getLogger( "aminopvr.Recorder" )

    STARTED     = 1
    NOT_STARTED = 2
    ABORTED     = 3
    FINISHED    = 4
    NOT_STOPPED = 5

    def __init__( self ):
        threading.Thread.__init__( self )

        self._logger.debug( "__init__" ) 

        self._messageHandler = {}
        self._messageHandler[_RecorderQueueItem.START_RECORDING]   = self._startRecording
        self._messageHandler[_RecorderQueueItem.STOP_RECORDING]    = self._stopRecording
        self._messageHandler[_RecorderQueueItem.ABORT_RECORDING]   = self._abortRecording
        self._messageHandler[_RecorderQueueItem.RECORDING_STARTED] = self._recordingStarted
        self._messageHandler[_RecorderQueueItem.RECORDING_STOPPED] = self._recordingStopped
        self._messageHandler[_RecorderQueueItem.RECORDING_ABORTED] = self._recordingAborted

    def stop( self, wait=False ):
        self._queue.put( _RecorderQueueItem( _RecorderQueueItem.STOP_RECORDER ) )
        if wait:
            self._queue.join()

    def startRecording( self, url, id_, filename, protocol, callback ):
        self._queue.put( _RecorderQueueItem( _RecorderQueueItem.START_RECORDING, ( url, id_, filename, protocol, callback ) ) )

    def stopRecording( self, id_ ):
        self._queue.put( _RecorderQueueItem( _RecorderQueueItem.STOP_RECORDING, (id_, ) ) )

    def abortRecording( self, id_ ):
        self._queue.put( _RecorderQueueItem( _RecorderQueueItem.ABORT_RECORDING, (id_, ) ) )

    def stopAllRecordings( self ):
        self._logger.warning( "Stopping all active recordings" )
        self._queue.put( _RecorderQueueItem( _RecorderQueueItem.STOP_ALL_RECORDINGS ) )

    def getActiveRecordings( self ):
        """
        Current implementation is wrong
        """
        self._logger.debug( "Recorder.getActiveRecordings" )
        activeRecordings = []
        for recording in self._recordings:
            activeRecordings.append( recording["recording"] )
        return activeRecordings

    def run( self ):
        running = True
        while running:
            item = self._queue.get()
            if item.id == _RecorderQueueItem.STOP_RECORDER:
                running = False
            elif item.id == _RecorderQueueItem.STOP_ALL_RECORDINGS:
                for id_ in self._recordings.keys():
                    self._stopRecording( id_ )
            elif item.id in self._messageHandler:
                self._messageHandler[item.id]( *item.data )
            self._queue.task_done()

    def _startRecording( self, url, id_, filename, protocol, callback ):
        """
        This can be much better. A 'cookie'-list makes searching for one troublesome and duplicate
        output files can easily happen.
        """
        self._logger.debug( "_startRecording: Start recording from url %s using protocol %s; filename: %s" % ( url, protocol, filename ) )

        if id_ in self._recordings:
            self._logger.error( "Recording with id %d already exists" % ( id ) )
            if callback:
                callback( id_, Recorder.NOT_STARTED )
        else:
            self._recordings[id_]                = {}
            self._recordings[id_]["outputFile"]  = filename
            self._recordings[id_]["callback"]    = callback
            self._recordings[id_]["recording"]   = ActiveRecording( id_, url, protocol, filename, self._recordingResult )
            self._recordings[id_]["recording"].start()

    def _stopRecording( self, id_ ):
        self._logger.debug( "_stopRecording( id=%d )" % ( id_ ) )
        self._stopAbortRecording( id_ )

    def _abortRecording( self, id_ ):
        self._logger.debug( "_abortRecording( id=%d )" % ( id_ ) )
        self._stopAbortRecording( id_, True )

    def _stopAbortRecording( self, id_, abort=False ):
        self._logger.debug( "_stopAbortRecording( id=%d, abort=%s )" % ( id_, abort ) )
        if not id_ in self._recordings:
            self._logger.error( "_stopAbortRecording: recording with id %d is not an active recording" % ( id_ ) )
        else:
            self._recordings[id_]["recording"].stop( abort )

    def _recordingStarted( self, id_ ):
        self._logger.debug( "_recordingStarted: id=%d" % ( id_ ) )
        if id_ in self._recordings:
            recording = self._recordings[id_]
            recording["callback"]( id_, Recorder.STARTED )
        else:
            self._logger.error( "_recordingStarted: recording with id=%d does not exist" % ( id ) )

    def _recordingStopped( self, id_ ):
        self._logger.debug( "_recordingStopped: id=%d" % ( id_ ) )
        if id_ in self._recordings:
            recording = self._recordings[id_]
            del self._recordings[id_]
            recording["callback"]( id_, Recorder.FINISHED )
        else:
            self._logger.error( "_recordingStopped: recording with id=%d does not exist" % ( id_ ) )

    def _recordingAborted( self, id_ ):
        self._logger.debug( "_recordingAborted: id=%d" % ( id_ ) )
        if id_ in self._recordings.has_key( id_ ):
            recording = self._recordings[id_]
            del self._recordings[id_]
            recording["callback"]( id_, Recorder.ABORTED )
        else:
            self._logger.error( "_recordingAborted: recording with id=%d does not exist" % ( id ) )

    def _recordingResult( self, id_, result ):
        self._logger.debug( "_recordingResult( id=%d, result=%s )" % ( id_, result ) )
        if result == ActiveRecording.STARTED:
            self._queue.put( _RecorderQueueItem( _RecorderQueueItem.RECORDING_STARTED, (id_, ) ) )
        elif result == ActiveRecording.FINISHED:
            self._queue.put( _RecorderQueueItem( _RecorderQueueItem.RECORDING_STOPPED, (id_, ) ) )
        elif result == ActiveRecording.ABORTED:
            self._queue.put( _RecorderQueueItem( _RecorderQueueItem.RECORDING_ABORTED, (id_, ) ) )
