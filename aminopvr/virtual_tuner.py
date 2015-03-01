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
from aminopvr.resource_monitor import Watchdog
from aminopvr.tools import printTraceback
import logging
import Queue
import threading
import uuid

MAX_ACTIVE_TUNERS       = 4
BUFFER_SIZE             = 40 * 188
LISTENER_FIFO_SIZE      = 100
WATCHDOG_KICK_PERIOD    = 5

class VirtualTuner( threading.Thread ):

    _logger       = logging.getLogger( "aminopvr.VirtualTuner" )
    _tunerLock    = threading.Lock()
    _activeTuners = []

    def __init__( self, url, protocol ):
        """
        Initialize 'VirtualTuner' instance.

        @param url:                 instance of ChannelUrl class
        @param protocol:            protocol to be used to get the input stream (e.g. multicast, http)
        """
        threading.Thread.__init__( self )

        self._url               = url
        self._protocol          = protocol

        self._running           = False

        self._listeners         = []
        self._listenerLock      = threading.RLock()

        self._logger.debug( "VirtualTuner.__init__( url=%s, protocol=%s )" % ( url, protocol ) )

    @classmethod
    def getTuner( cls, url, protocol ):
        tuner = None
        with cls._tunerLock:
            for activeTuner in cls._activeTuners:
                if activeTuner["url"] == url and activeTuner["protocol"] == protocol:
                    cls.info( "VirtualTuner.getTuner: found active tuner" )
                    tuner = activeTuner["tuner"]
                    break
            if not tuner:
                if len( cls._activeTuners ) <= MAX_ACTIVE_TUNERS:
                    activeTuner             = {}
                    activeTuner["url"]      = url
                    activeTuner["protocol"] = protocol
                    activeTuner["tuner"]    = cls( url, protocol )
                    tuner = activeTuner["tuner"]
                else:
                    cls._logger.error( "VirtualTuner.getTuner: too many tuner instances" )
        return tuner

    def addListener( self, id_, callback=None ):
        listener               = {}
        listener["id"]         = id_
        listener["callback"]   = callback

        # create a FIFO queue if no callback is specified; listener will read from tuner
        if not callback:
            listener["fifo"]   = Queue.Queue( maxsize=LISTENER_FIFO_SIZE )

        with self._listenerLock:
            self._listeners.append( listener )

        if not self._running:
            self._logger.info( "VirtualTuner.addListener(): start tuner" )
            self._running = True
            super( VirtualTuner, self ).start()

    def removeListener( self, id_ ):
        self._logger.debug( "VirtualTuner.removeListener( id=%d )" % ( id_ ) )

        with self._listenerLock:
            for listener in self._listeners:
                if listener["id"] == id_:
                    self._logger.info( "VirtualTuner.removeListener(): remove listener" )
                    self._listeners.remove( listener )
                    break

            numListeners = len( self._listeners )
            self._logger.info( "VirtualTuner.removeListener: number of listeners=%d" % ( numListeners ) )

        if self._running and numListeners == 0:
            self._terminateTuner()
            if self.isAlive():
                self._running = False
                try:
                    self.join( 5.0 )
                except:
                    pass
                if self.isAlive():
                    self._logger.critical( "VirtualTuner._terminateTuner(): unable to stop tuner!" )

    def read( self, id_ ):
        data = None
        fifo = None
        with self._listenerLock:
            for listener in self._listeners:
                if listener["id"] == id_:
                    if "fifo" in listener:
                        fifo = listener["fifo"]
                    else:
                        self._logger.error( "VirtualTuner.read(): no FIFO for this listener; uses callback to feed data")
                        self.removeListener( id_ )
                    break

        if fifo:
            try:
                data = listener["fifo"].get( True, 5.0 )
            except Queue.Empty:
                self._logger.debug( "VirtualTuner.read(): FIFO is (still) empty" )

        return data

    def _terminateTuner( self ):
        with self._listenerLock:
            self._listeners = []
        
        with self._tunerLock:
            for activeTuner in self._activeTuners:
                if activeTuner["url"] == self._url and activeTuner["protocol"] == self._protocol:
                    self._activeTuners.remove( activeTuner )
                    break

    def run( self ):
        try:
            inputStream = InputStreamAbstract.createInputStream( self._protocol, self._url )
            if inputStream:
                if inputStream.open():
                    self._logger.info( "VirtualTuner.run: start reading from %s on protocol %d" % ( self._url, self._protocol ) )
    
                    watchdogId = uuid.uuid1()
                    def watchdogTimeout():
                        self._logger.warning( "VirtualTuner.run: watchdog timed out; close stream; remove watchdog %s" % ( watchdogId ) )
                        if inputStream:
                            inputStream.close()
                            inputStream = None
                        Watchdog().remove( watchdogId )
                        self._terminateTuner()
    
                    Watchdog().add( watchdogId, watchdogTimeout )
                    Watchdog().kick( watchdogId, WATCHDOG_KICK_PERIOD )
        
                    while self._running and len( self._listeners ) > 0:
                        data = inputStream.read( BUFFER_SIZE )
        
                        # If date == None, then there was a timeout
                        if data:
                            Watchdog().kick( watchdogId, WATCHDOG_KICK_PERIOD )
                            with self._listenerLock:
                                for listener in self._listeners:
                                    if listener["callback"]:
                                        listener["callback"]( data )
                                    else:
                                        try:
                                            listener["fifo"].put( data, True, 1.0 )
                                        except Queue.Full:
                                            self._logger.info( "VirtualTuner.run: listener's queue full, remove listener" )
                                            self._listeners.remove( listener )
        
                    inputStream.close()
                    inputStream = None
                    Watchdog().remove( watchdogId )
                    self._terminateTuner()
                else:
                    self._logger.critical( "VirtualTuner.run: Could not open input stream with url=%r on protocol=%d" % ( self._url, self._protocol ) )
                    self._terminateTuner()
            else:
                self._logger.critical( "VirtualTuner.run: Could not create input stream with url=%r on protocol=%d" % ( self._url, self._protocol ) )
                self._terminateTuner()

        except:
            self._logger.error( "VirtualTuner.run: error while reading from %s on protocol=%d" % ( self._url, self._protocol ) )
            printTraceback()
            if inputStream:
                inputStream.close()
            self._terminateTuner()
