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
import datetime
import logging
import threading
import time

class Timer( threading.Thread ):

    """
    Timer class

    Each timer instance is a thread that fires 1 or more events at configured times.
    For scheduled recordings, two events will be registered. For others one event with
    'recurrenceInterval' to allow automatic resetting of the event after it has fired.
    A timer event can be changed if it hasn't fired yet. If a timer is stopped it is possible
    to fire the last configured event with 'CANCEL_TIMER_EVENT' event type.
    The standard Timer class in Python doesn't fully support changing trigger times.
    """
    _logger = logging.getLogger( "aminopvr.Timer" )

    TIME_TRIGGER_EVENT = 1
    TIMER_ENDED_EVENT  = 2
    CANCEL_TIMER_EVENT = 3

    def __init__( self, timers, pollInterval=10.0, recurrenceInterval=None ):
        threading.Thread.__init__( self )

        self._logger.debug( "Timer.__init__( timers=%s )" % ( timers ) )

        self._lock               = threading.Lock()
        self._events             = []
        self._pollInterval       = pollInterval
        self._recurrenceInterval = recurrenceInterval
        self._running            = True

        lastTime = 0
        for timer in timers:
            if lastTime != 0:
                if timer["time"] < lastTime:
                    self._logger.critical( "Timer.__init__: timers not in ascending order" )
                    return
            lastTime = timer["time"]

        for timer in timers:
            event = {
                        "time":              timer["time"],
                        "callback":          timer["callback"],
                        "callbackArguments": timer["callbackArguments"],
                        "triggered":         False
                    }
            self._events.append( event )

        self.start()

    def __repr__( self ):
        return "Timer( events=%r )" % ( self._events )

    def changeTimer( self, index, time ):
        self._logger.debug( "Timer.changeTimer( index=%s, time=%s )" % ( index, time ) )

        if index > len( self._events ):
            self._logger.critical( "Timer.changeTimer: index out of bounds" )
            return

        if index > 0:
            previousTimer = self._events[index - 1]["time"]
            if time <= previousTimer:
                self._logger.critical( "Timer.changeTimer: timer %s on/before previous timer %s" % ( time, previousTimer ) )
                return
        if index + 1 <= len( self._events ):
            nextTimer = self._events[index + 1]["time"]
            if time >= nextTimer:
                self._logger.critical( "Timer.changeTimer: timer %s on/after next timer %s" % ( time, nextTimer ) )
                return

        with self._lock:
            if not self._events[index]["triggered"]:
                self._events[index]["time"] = time
            else:
                self._logger.warning( "Timer.changeTimer: start event has already passed; ignoring request." )

    def run( self ):
        self._logger.debug( "Timer.run: starting timers" )

        numTriggered = 0

        while self._running and numTriggered < len( self._events ):
            now = datetime.datetime.now()
            for event in self._events:
                with self._lock:
                    if not event["triggered"] and now >= event["time"]:
                        self._logger.debug( "Timer.run: event @ %s triggered (now %s)" % ( event["time"], now ) )
                        event["callback"]( Timer.TIME_TRIGGER_EVENT, event["callbackArguments"] )
                        if not self._recurrenceInterval:
                            event["triggered"] = True
                            numTriggered += 1
                        else:
                            event["time"] = event["time"] + self._recurrenceInterval
                            self._logger.warning( "Timer.run: Resetting timer, next event will fire at %s" % ( event["time"] ) )
            time.sleep( self._pollInterval )
        self._logger.debug( "Timer.run: timers ended" )
        event["callback"]( Timer.TIMER_ENDED_EVENT, None )

    def stop( self, triggerLast=False ):
        self._logger.debug( "Timer.stop" )
        self._running = False
        if self.isAlive():
            self.join()
        if triggerLast:
            lastEvent = self._events[len( self._events ) - 1] 
            lastEvent["callback"]( Timer.CANCEL_TIMER_EVENT, lastEvent["callbackArguments"] )
