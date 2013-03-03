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

    def __init__( self, recordingId, url, protocol, outputFile, callback, callbackArguments ):
        """
        Initialize 'ActiveRecording' instance.

        @param recordingId:         identification of recording for callbacks
        @param url:                 instance of ChannelUrl class
        @param protocol:            protocol to be used to get the input stream (e.g. multicast, http)
        @param callback:            callback function for recording events
        @param callbackArguments:   callback context (we may not need this, as recordingId + outputFile
                                    is uniquely identifying the specific recording)
        """
        threading.Thread.__init__( self )

        self._recordingId       = recordingId
        self._url               = url
        self._protocol          = protocol
        self._outputFiles       = [ outputFile ]
        self._callback          = callback
        self._callbackArguments = callbackArguments

        self._outputFileLock    = threading.Lock()
        self._running           = False

        self._newOutputFile     = ""
        self._oldOutputFile     = ""

        self._logger.debug( "ActiveRecording.__init__( recordingId=%s, url=%s, protocol=%s, outputFile=%s, callback=%s, callbackArguments=%s )" % ( recordingId, url, protocol, outputFile, callback, callbackArguments ) )

        if not self._callback:
            self._logger.critical( "ActiveRecording.__init__: no callback specified" )

    def start( self ):
        self._logger.debug( "ActiveRecording.start" )
        self._running = True
        super( ActiveRecording, self ).start()

    def stop( self, outputFile="" ):
        self._logger.debug( "ActiveRecording.stop( outputFile=%s )" % ( outputFile ) )

        if outputFile or len( self._outputFiles ) == 1:
            self._running = False
            self.join( 3.0 )
            if self.isAlive():
                self._logger.error( "ActiveRecording.stop: thread not stopping in time; kill it!" )
            return not self.isAlive()
        else:
            while self._newOutputFile != "":
                time.sleep( 0.1 )
            with self._outputFileLock:
                self._oldOutputFile = outputFile
            return True

    def addOutputFile( self, outputFile ):
        while self._newOutputFile != "":
            time.sleep( 0.1 )
        with self._outputFileLock:
            self._newOutputFile = outputFile

    def run( self ):
        inputStream = InputStreamAbstract.createInputStream( self._protocol, self._url )
        if inputStream and inputStream.open():
            self._logger.debug( "ActiveRecording.run: start recording for recordingId=%s, file=%s" % ( self._recordingId, self._outputFiles[0] ) )
            self._callback( self._callbackArguments, self._recordingId, self._outputFiles[0], ActiveRecording.STARTED )
            while self._running:
                inputStream.read( 10240 )
    
                time.sleep( 0.01 )
    
                if self._oldOutputFile != "":
                    with self._outputFileLock:
                        self._logger.debug( "ActiveRecording.run: loop: finished recording for recordingId=%s, file=%s" % ( self._recordingId, self._oldOutputFile ) )
                        self._callback( self._callbackArguments, self._recordingId, self._oldOutputFile, ActiveRecording.FINISHED )
                        self._outputFiles.remove( self._oldOutputFile )
                        self._oldOutputFile = ""
                if self._newOutputFile != "":
                    with self._outputFileLock:
                        self._logger.debug( "ActiveRecording.run: loop: start recording for recordingId=%s, file=%s" % ( self._recordingId, self._newOutputFile ) )
                        self._callback( self._callbackArguments, self._recordingId, self._newOutputFile, ActiveRecording.STARTED )
                        self._outputFiles.append( self._newOutputFile )
                        self._newOutputFile = ""
            inputStream.close()
            with self._outputFileLock:
                for outputFile in self._outputFiles:
                    self._logger.debug( "ActiveRecording.run: finished recording for recordingId=%s, file=%s" % ( self._recordingId, outputFile ) )
                    self._callback( self._callbackArguments, self._recordingId, outputFile, ActiveRecording.FINISHED )
        else:
            self._logger.critical( "ActiveRecording.run: Could not create or open url=%r on protocol=%d for recordingId=%s" % ( self._url, self._protocol, self._recordingId ) )
            self._callback( self._callbackArguments, self._recordingId, self._outputFiles[0], ActiveRecording.ABORTED )

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

    _activeRecordings = dict()
    _lock             = threading.Lock()
    _logger           = logging.getLogger( "aminopvr.Recorder" )

    STARTED  = 1
    ABORTED  = 2
    FINISHED = 3

    def __init__( self ):
        self._logger.debug( "__init__" ) 

    def startRecording( self, url, timerId, filename, protocol, callback ):
        """
        This can be much better. A 'cookie'-list makes searching for one troublesome and duplicate
        output files can easily happen.
        """
        self._logger.debug( "Start recording from url %s using protocol %s; filename: %s" % ( url, protocol, filename ) )
        recordingId = self._createId( url, protocol )
        with self._lock:
            if self._activeRecordings.has_key( recordingId ):
                self._logger.warning( "Recording with recordingId %s already running" % ( recordingId ) )
                self._activeRecordings[recordingId]["activeRecording"].addOutputFile( filename )
            else:
                activeRecording = ActiveRecording( recordingId, url, protocol, filename, Recorder._recordingResult, self )
                activeRecording.start()
                self._activeRecordings[recordingId] = {}
                self._activeRecordings[recordingId]["activeRecording"] = activeRecording
                self._activeRecordings[recordingId]["cookie"]    = []
            self._activeRecordings[recordingId]["cookie"].append( {
                                                                    "timerId":    timerId,
                                                                    "outputFile": filename,
                                                                    "callback":   callback
                                                                  } )
        return recordingId

    def stopRecording( self, recordingId, timerId=None ):
        self._logger.debug( "Recorder.stopRecording( recordingId=%s, timerId=%d )" % ( recordingId, timerId ) )
        if not self._activeRecordings.has_key( recordingId ):
            self._logger.error( "stopRecording: recordingId %s is not an active recording" % ( recordingId ) )
        else:
            recordingFilename = ""
            if timerId:
                with self._lock:
                    for i in range( len( self._activeRecordings[recordingId]["cookie"] ) ):
                        activeRecording = self._activeRecordings[recordingId]["cookie"][i]
                        if timerId == activeRecording["timerId"]:
                            recordingFilename = activeRecording["outputFile"]

            if not self._activeRecordings[recordingId]["activeRecording"].stop( recordingFilename ):
                self._logger.debug( "stopRecording: Recording thread didn't end properly, we're going to delete the object anyway" )
                with self._lock:
                    for i in range( len( self._activeRecordings[recordingId]["cookie"] ) ):
                        activeRecording = self._activeRecordings[recordingId]["cookie"][i]
                        if not timerId or timerId == activeRecording["timerId"]:
                            activeRecording["callback"]( Recorder.ABORTED, activeRecording["timerId"] )
                            self._activeRecordings[recordingId]["cookie"].pop( i )
                            self._logger.debug( "stopRecording: removed outputFile and decreased refCount" )
                    if len( self._activeRecordings[recordingId]["cookie"] ) == 0:
                        del self._activeRecordings[recordingId]
                        self._logger.debug( "stopRecording: : no more listeners; removed recordingId" )

    def stopAllRecordings( self ):
        self._logger.warning( "Stopping all active recordings" )
        for recordingId in self._activeRecordings.keys():
            self.stopRecording( recordingId )

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

    def _recordingResult( self, recordingId, outputFile, result ):
        self._logger.debug( "Recorder._recordingResult( recordingId=%s, outputFile=%s, result=%s )" % ( recordingId, outputFile, result ) )
        if result == ActiveRecording.STARTED:
            self._logger.debug( "Recorder._recordingResult: ActiveRecording.STARTED" )
            with self._lock:
                for i in range( len( self._activeRecordings[recordingId]["cookie"] ) ):
                    recording = self._activeRecordings[recordingId]["cookie"][i]
                    if outputFile == recording["outputFile"]:
                        recording["callback"]( recording["timerId"], Recorder.STARTED )
        elif result == ActiveRecording.ABORTED or result == ActiveRecording.FINISHED:
            with self._lock:
                for i in range( len( self._activeRecordings[recordingId]["cookie"] ) ):
                    recording = self._activeRecordings[recordingId]["cookie"][i]
                    if outputFile == recording["outputFile"]:
                        if result == result == ActiveRecording.FINISHED:
                            recording["callback"]( recording["timerId"], Recorder.FINISHED )
                        else:
                            recording["callback"]( recording["timerId"], Recorder.ABORTED )
                        self._activeRecordings[recordingId]["cookie"].pop( i )
                        self._logger.debug( "Recorder._recordingResult: removed outputFile and decreased refCount" )
                if len( self._activeRecordings[recordingId]["cookie"] ) == 0:
                    del self._activeRecordings[recordingId]
                    self._logger.debug( "Recorder._recordingResult: no more listeners; removed recordingId" )


