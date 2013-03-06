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
import logging
import threading
import time

class ActiveRecording( threading.Thread ):

    """
    An instance of this class handles recording of one 'url'
    By default / Initially there is one output file attached to the recording, but it is
    possible the add/remove output files while active. This is to handle overlapping programs
    from a single source. Overlap may be caused by recordings which are requested to start
    early / end late or manual recordings.

    I'm not super pleased with the current implementation of handling added/removed output
    files

    TODO:
    - The actual stream reading an saving it in output file(s)
    - Event callback (started, finished, error, etc)
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
        self._listenerLock      = threading.Lock()

        self._newOutputFile     = ""
        self._oldOutputFile     = ""

        self._logger.debug( "ActiveRecording.__init__( url=%s, protocol=%s )" % ( url, protocol ) )

        if not self._callback:
            self._logger.critical( "ActiveRecording.__init__: no callback specified" )

    def start( self ):
        self._logger.debug( "ActiveRecording.start" )
        self._running = True
        super( ActiveRecording, self ).start()

    def stop( self ):
        self._logger.debug( "ActiveRecording.stop()" )

        with self._listenerLock:
            for listener in self._listeners:
                self._logger.critical( "ActiveRecording.stop: listener with id %d is still there; abort" % ( listener["id"] ) )
                listener["callback"]( listener["id"], ActiveRecording.ABORTED )
                self._listeners.remove( listener )

        self._running = False
        self.join( 5.0 )
        if self.isAlive():
            self._logger.critical( "ActiveRecording.stop: thread not stopping in time; kill it!" )
        return not self.isAlive()
                    
    def addListener( self, id, outputFile, callback ):
        with self._listenerLock:
            listener               = {}
            listener["id"]         = id
            listener["outputFile"] = outputFile
            listener["callback"]   = callback
            listener["new"]        = True
            self._listeners.append( listener )

    def removeListener( self, id ):
        self._logger.debug( "ActiveRecording.removeListener( id=%d )" % ( id ) )

        with self._listenerLock:
            for listener in self._listeners:
                if listener["id"] == id:
                    listener["callback"]( listener["id"], ActiveRecording.FINISHED )
                    self._listeners.remove( listener )
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
                                listener["callback"]( listener["id"], ActiveRecording.STARTED )
                                listener["new"] = False

            inputStream.close()
            with self._listenerLock:
                for listener in self._listeners:
                    self._logger.warning( "ActiveRecording.run: we've finished streaming, but there are still listener with id %d attached" % ( listener["id"] ) )
                    listener["callback"]( listener["id"], ActiveRecording.ABORTED )
                    self._listeners.remove( listener )
        else:
            self._logger.critical( "ActiveRecording.run: Could not create or open url=%r on protocol=%d" % ( self._url, self._protocol ) )
            with self._listenerLock:
                for listener in self._listeners:
                    listener["callback"]( listener["id"], ActiveRecording.ABORTED )
                    self._listeners.remove( listener )

class Recorder( object ):
    """
    Singleton class that is the arbiter for all (active) recordings.

    New recordings are added through startRecording
    Recordings can be stopped through stopRecording

    TODO:
    - startRecording need instance of recording.Recording to change status of recording issued
      by Recording callbacks
    - getActiveRecordings should return list of recording.Recording
    - Event callback from Recording and towards caller 
    """
    __metaclass__ = Singleton

    _recordings       = dict()
    _activeRecordings = dict()
    _lock             = threading.Lock()
    _logger           = logging.getLogger( "aminopvr.Recorder" )

    STARTED  = 1
    ABORTED  = 2
    FINISHED = 3

    def __init__( self ):
        self._logger.debug( "__init__" ) 

    def startRecording( self, url, id, filename, protocol, callback ):
        """
        This can be much better. A 'cookie'-list makes searching for one troublesome and duplicate
        output files can easily happen.
        """
        self._logger.debug( "Start recording from url %s using protocol %s; filename: %s" % ( url, protocol, filename ) )
        recordingId = self._createId( url, protocol )
        with self._lock:
            if self._recordings.has_key( id ):
                self._logger.error( "Recording with id %d already exists" % ( id ) )
                return False
            else:
                if self._activeRecordings.has_key( recordingId ):
                    self._logger.warning( "Recording with recordingId %s already running; add this one" % ( recordingId ) )
                    self._activeRecordings[recordingId].addListener( id, filename, self._recordingResult )
                else:
                    self._activeRecordings[recordingId] = ActiveRecording( url, protocol )
                    self._activeRecordings[recordingId].addListener( id, filename, self._recordingResult )
                    self._activeRecordings[recordingId].start()
                self._recordings[id] = {}
                self._recordings[id]["recordingId"] = recordingId
                self._recordings[id]["outputFile"]  = filename
                self._recordings[id]["callback"]    = callback
        return True

    def stopRecording( self, id ):
        self._logger.debug( "Recorder.stopRecording( id=%d )" % ( id ) )
        if not self._recordings.has_key( id ):
            self._logger.error( "stopRecording: recording with id %d is not an active recording" % ( id ) )
            return False
        else:
            with self._lock:
                recordingId = self._recordings[id]["recordingId"]

            if recordingId != "" and self._activeRecordings.has_key( recordingId ):
                if self._activeRecordings[recordingId].removeListener( id ) == 0:
                    self._logger.debug( "stopRecording: No more listeners; stop ActiveRecorder" )
                    if not self._activeRecordings[recordingId].stop():
                        self._logger.debug( "stopRecording: Recording thread didn't end properly, we're going to delete the object anyway" )
                        with self._lock:
                            del self._activeRecordings[recordingId]
                        return False
            else:
                self._logger.error( "stopRecording: recordingId is not available" )
                return False
        return True

    def stopAllRecordings( self ):
        self._logger.warning( "Stopping all active recordings" )
        for id in self._recordings.keys():
            self.stopRecording( id )

    def getActiveRecordings( self ):
        """
        Current implementation is wrong
        """
        self._logger.debug( "Recorder.getActiveRecordings" )
        activeRecordings = []
        for recording in self._activeRecordings:
            activeRecordings.append( recording )
        return activeRecordings

    def _createId( self, url, protocol ):
        """
        WIP
        """
        return "%s_%d" % ( url.ip, protocol )

    def _recordingResult( self, id, result ):
        self._logger.debug( "Recorder._recordingResult( id=%d, result=%s )" % ( id, result ) )
        if result == ActiveRecording.STARTED:
            self._logger.debug( "Recorder._recordingResult: ActiveRecording.STARTED" )
            with self._lock:
                if self._recordings.has_key( id ):
                    recording = self._recordings[id]
                    recording["callback"]( recording["id"], Recorder.STARTED )
        elif result == ActiveRecording.ABORTED or result == ActiveRecording.FINISHED:
            with self._lock:
                if self._recordings.has_key( id ):
                    recording = self._recordings[id]
                    if result == ActiveRecording.FINISHED:
                        recording["callback"]( recording["id"], Recorder.FINISHED )
                    else:
                        recording["callback"]( recording["id"], Recorder.ABORTED )
                    del self._recordings[id]
