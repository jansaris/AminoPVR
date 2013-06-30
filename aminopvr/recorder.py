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
from aminopvr.input_stream import InputStreamAbstract
from aminopvr.tools import Singleton
from Queue import Queue
import logging
import threading

class ActiveRecording( threading.Thread ):

    """
    An instance of this class handles recording of one 'url'
    By default / Initially there is one output file attached to the recording, but it is
    possible the add/remove output files while active. This is to handle overlapping programs
    from a single source. Overlap may be caused by recordings which are requested to start
    early / end late or manual recordings.

    I'm not super pleased with the current implementation of handling added/removed output
    files
    """

    _logger = logging.getLogger( "aminopvr.ActiveRecording" )

    STARTED  = 1
    ABORTED  = 2
    FINISHED = 3

    def __init__( self, url, protocol ):
        """
        Initialize 'ActiveRecording' instance.

        @param url:                 instance of ChannelUrl class
        @param protocol:            protocol to be used to get the input stream (e.g. multicast, http)
        """
        threading.Thread.__init__( self )

        self._url               = url
        self._protocol          = protocol

        self._running           = False

        self._listeners         = []
        self._listenerLock      = threading.RLock()

        self._logger.debug( "ActiveRecording.__init__( url=%s, protocol=%s )" % ( url, protocol ) )

    def start( self ):
        self._logger.debug( "ActiveRecording.start" )
        self._running = True
        super( ActiveRecording, self ).start()

    def stop( self ):
        self._logger.debug( "ActiveRecording.stop()" )

        self._listenerLock.acquire()
        listeners = list( self._listeners )
        self._listenerLock.release()

        for listener in listeners:
            self._logger.critical( "ActiveRecording.stop: listener with id %d is still there; abort" % ( listener["id"] ) )
            with self._listenerLock:
                if listener in self._listeners:
                    self._listeners.remove( listener )
            if "output" in listener:
                listener["output"].close()
            if listener.has_key( "callback" ) and listener["callback"]:
                listener["callback"]( listener["id"], ActiveRecording.ABORTED )

        self._running = False
        self.join( 5.0 )
        if self.isAlive():
            self._logger.critical( "ActiveRecording.stop: thread not stopping in time; kill it!" )
        return not self.isAlive()
                    
    def addListener( self, id, outputFile, callback ):
        listener               = {}
        listener["id"]         = id
        listener["outputFile"] = outputFile
        listener["callback"]   = callback
        listener["new"]        = True
        with self._listenerLock:
            self._listeners.append( listener )

    def removeListener( self, id ):
        self._logger.debug( "ActiveRecording.removeListener( id=%d )" % ( id ) )

        with self._listenerLock:
            for listener in self._listeners:
                if listener["id"] == id:
                    self._logger.info( "ActiveRecording.removeListener: remove listener" )
                    self._listeners.remove( listener )
                    if "output" in listener:
                        listener["output"].close()
                    if listener.has_key( "callback" ) and listener["callback"]:
                        listener["callback"]( listener["id"], ActiveRecording.FINISHED )
        self._logger.info( "ActiveRecording.removeListener: number of listeners=%d" % ( len( self._listeners ) ) )
        return len( self._listeners )

    def run( self ):
        inputStream = InputStreamAbstract.createInputStream( self._protocol, self._url )
        if inputStream and inputStream.open():
            self._logger.debug( "ActiveRecording.run: start recording from %s" % ( self._url ) )
            while self._running:
                data = inputStream.read( 16 * 1024 )

                # If date == None, then there was a timeout
                if data:
                    with self._listenerLock:
                        for listener in self._listeners:
                            """ Write data to listener["outputFile"] """
                            if listener["new"]:
                                listener["new"] = False
                                try:
                                    listener["output"] = open( listener["outputFile"], "wb" )
                                    if listener.has_key( "callback" ) and listener["callback"]:
                                        listener["callback"]( listener["id"], ActiveRecording.STARTED )
                                except:
                                    if listener.has_key( "callback" ) and listener["callback"]:
                                        listener["callback"]( listener["id"], ActiveRecording.ABORTED )
                            if "output" in listener:
                                listener["output"].write( data )

            inputStream.close()
            with self._listenerLock:
                for listener in self._listeners:
                    self._logger.warning( "ActiveRecording.run: we've finished streaming, but there are still listener with id %d attached" % ( listener["id"] ) )
                    self._listeners.remove( listener )
                    if listener.has_key( "callback" ) and listener["callback"]:
                        listener["callback"]( listener["id"], ActiveRecording.ABORTED )
        else:
            self._logger.critical( "ActiveRecording.run: Could not create or open url=%r on protocol=%d" % ( self._url, self._protocol ) )
            with self._listenerLock:
                for listener in self._listeners:
                    self._listeners.remove( listener )
                    if listener.has_key( "callback" ) and listener["callback"]:
                        listener["callback"]( listener["id"], ActiveRecording.ABORTED )

class _RecorderQueueItem( object ):
    STOP_RECORDER       = 1
    STOP_ALL_RECORDINGS = 2
    START_RECORDING     = 3
    STOP_RECORDING      = 4
    RECORDING_STARTED   = 5
    RECORDING_STOPPED   = 6
    RECORDING_ABORTED   = 7
    def __init__( self, id, data=None ):
        self.id   = id
        self.data = data

class Recorder( threading.Thread ):
    """
    Singleton class that is the arbiter for all (active) recordings.

    New recordings are added through startRecording
    Recordings can be stopped through stopRecording
    """
    __metaclass__ = Singleton

    _recordings       = dict()
    _activeRecordings = dict()
    _queue            = Queue()
    _logger           = logging.getLogger( "aminopvr.Recorder" )

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
        self._messageHandler[_RecorderQueueItem.RECORDING_STARTED] = self._recordingStarted
        self._messageHandler[_RecorderQueueItem.RECORDING_STOPPED] = self._recordingStopped
        self._messageHandler[_RecorderQueueItem.RECORDING_ABORTED] = self._recordingAborted

    def stop( self, wait=False ):
        self._queue.put( _RecorderQueueItem( _RecorderQueueItem.STOP_RECORDER ) )
        if wait:
            self._queue.join()

    def startRecording( self, url, id, filename, protocol, callback ):
        self._queue.put( _RecorderQueueItem( _RecorderQueueItem.START_RECORDING, ( url, id, filename, protocol, callback ) ) )

    def stopRecording( self, id ):
        self._queue.put( _RecorderQueueItem( _RecorderQueueItem.STOP_RECORDING, (id, ) ) )

    def stopAllRecordings( self ):
        self._logger.warning( "Stopping all active recordings" )
        self._queue.put( _RecorderQueueItem( _RecorderQueueItem.STOP_ALL_RECORDINGS ) )

    def getActiveRecordings( self ):
        """
        Current implementation is wrong
        """
        self._logger.debug( "Recorder.getActiveRecordings" )
        activeRecordings = []
        for recording in self._activeRecordings:
            activeRecordings.append( recording )
        return activeRecordings

    def run( self ):
        running = True
        while running:
            item = self._queue.get()
            if item.id == _RecorderQueueItem.STOP_RECORDER:
                running = False
            elif item.id == _RecorderQueueItem.STOP_ALL_RECORDINGS:
                for id in self._recordings.keys():
                    self._stopRecording( id )
            elif self._messageHandler.has_key( item.id ):
                self._messageHandler[item.id]( *item.data )
            self._queue.task_done()

    def _startRecording( self, url, id, filename, protocol, callback ):
        """
        This can be much better. A 'cookie'-list makes searching for one troublesome and duplicate
        output files can easily happen.
        """
        self._logger.debug( "_startRecording: Start recording from url %s using protocol %s; filename: %s" % ( url, protocol, filename ) )
        recordingId = self._createId( url, protocol )
        if self._recordings.has_key( id ):
            self._logger.error( "Recording with id %d already exists" % ( id ) )
            if callback:
                callback( id, Recorder.NOT_STARTED )
        else:
            if self._activeRecordings.has_key( recordingId ):
                self._logger.warning( "_startRecording: Recording with recordingId %s already running; add this one" % ( recordingId ) )
                self._activeRecordings[recordingId].addListener( id, filename, self._recordingResult )
            else:
                self._activeRecordings[recordingId] = ActiveRecording( url, protocol )
                self._activeRecordings[recordingId].addListener( id, filename, self._recordingResult )
                self._activeRecordings[recordingId].start()
            self._recordings[id] = {}
            self._recordings[id]["recordingId"] = recordingId
            self._recordings[id]["outputFile"]  = filename
            self._recordings[id]["callback"]    = callback

    def _stopRecording( self, id ):
        self._logger.debug( "_stopRecording( id=%d )" % ( id ) )
        if not self._recordings.has_key( id ):
            self._logger.error( "_stopRecording: recording with id %d is not an active recording" % ( id ) )
        else:
            recordingId = self._recordings[id]["recordingId"]

            self._logger.debug( "_stopRecording: recordingId=%s" % ( recordingId ) )

            if recordingId != "" and self._activeRecordings.has_key( recordingId ):
                if self._activeRecordings[recordingId].removeListener( id ) == 0:
                    self._logger.warning( "_stopRecording: No more listeners; stop ActiveRecorder" )
                    if not self._activeRecordings[recordingId].stop():
                        self._logger.debug( "stopRecording: Recording thread didn't end properly, we're going to delete the object anyway" )
                    del self._activeRecordings[recordingId]
            else:
                self._logger.error( "_stopRecording: recordingId is not available" )
                if self._recordings[id]["callback"]:
                    self._recordings[id]["callback"]( id, Recorder.NOT_STOPPED )
                del self._recordings[id]

    def _recordingStarted( self, id ):
        self._logger.debug( "_recordingStarted: id=%d" % ( id ) )
        if self._recordings.has_key( id ):
            recording = self._recordings[id]
            recording["callback"]( id, Recorder.STARTED )
        else:
            self._logger.error( "_recordingStarted: recording with id=%d does not exist" % ( id ) )

    def _recordingStopped( self, id ):
        self._logger.debug( "_recordingStopped: id=%d" % ( id ) )
        if self._recordings.has_key( id ):
            recording = self._recordings[id]
            del self._recordings[id]
            recording["callback"]( id, Recorder.FINISHED )
        else:
            self._logger.error( "_recordingStopped: recording with id=%d does not exist" % ( id ) )

    def _recordingAborted( self, id ):
        self._logger.debug( "_recordingAborted: id=%d" % ( id ) )
        if self._recordings.has_key( id ):
            recording = self._recordings[id]
            del self._recordings[id]
            recording["callback"]( id, Recorder.ABORTED )
        else:
            self._logger.error( "_recordingAborted: recording with id=%d does not exist" % ( id ) )

    def _recordingResult( self, id, result ):
        self._logger.debug( "_recordingResult( id=%d, result=%s )" % ( id, result ) )
        if result == ActiveRecording.STARTED:
            self._queue.put( _RecorderQueueItem( _RecorderQueueItem.RECORDING_STARTED, (id, ) ) )
        elif result == ActiveRecording.FINISHED:
            self._queue.put( _RecorderQueueItem( _RecorderQueueItem.RECORDING_STOPPED, (id, ) ) )
        elif result == ActiveRecording.ABORTED:
            self._queue.put( _RecorderQueueItem( _RecorderQueueItem.RECORDING_ABORTED, (id, ) ) )

    def _createId( self, url, protocol ):
        """
        WIP
        """
        return "%s_%d" % ( url.ip, protocol )
