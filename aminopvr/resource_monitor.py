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
from aminopvr.timer import Timer
from aminopvr.tools import Singleton, getTimestamp
import datetime
import logging
import threading

class Watchdog( object ):
    __metaclass__ = Singleton

    __instance = None

    _logger = logging.getLogger( "aminopvr.Watchdog" )

    def __init__( self ):
        self._watchdogLock  = threading.RLock()
        self._watchdogs     = {};

        now                 = datetime.datetime.now()
        watchdogInterval    = datetime.timedelta( seconds=2 )
        watchdogTime        = now + watchdogInterval

        self._logger.warning( "Starting Watchdog timer @ %s with interval %s" % ( watchdogTime, watchdogInterval ) )

        self._timer = Timer( [ { "time": watchdogTime, "callback": self._timerCallback, "callbackArguments": None } ], pollInterval=0.5, recurrenceInterval=watchdogInterval )

        Watchdog.__instance = self

    def stop( self ):
        self._logger.warning( "Stopping Watchdog" )
        self._timer.stop()
        with self._watchdogLock:
            for watchdogId in self._watchdogs:
                self._logger.info( "Notify watchdog %s" % ( watchdogId ) )
                watchdog = self._watchdogs[watchdogId]
                if "callback" in watchdog:
                    callback = watchdog["callback"]
                    callback()

    def add( self, watchdogId, callback ):
        with self._watchdogLock:
            if not watchdogId in self._watchdogs:
                self._watchdogs[watchdogId] = { "callback": callback, "lastkick": 0 }
            else:
                self._logger.error( "Watchdog %s already exists" % ( watchdogId ) )

    def kick( self, watchdogId, kick ):
        with self._watchdogLock:
            if watchdogId in self._watchdogs:
                self._watchdogs[watchdogId]["lastkick"] = getTimestamp() + kick
            else:
                self._logger.error( "Watchdog %s does not exists" % ( watchdogId ) )

    def remove( self, watchdogId ):
        with self._watchdogLock:
            if watchdogId in self._watchdogs:
                del self._watchdogs[watchdogId]
            else:
                self._logger.error( "Watchdog %s does not exists" % ( watchdogId ) )
        
    def _timerCallback( self, event, arguments ):
        now = getTimestamp()

        expiredWatchdogId = None
        with self._watchdogLock:
            for watchdogId in self._watchdogs:
                watchdog = self._watchdogs[watchdogId]
                if watchdog["lastkick"] != 0 and watchdog["lastkick"] < now:
                    expiredWatchdogId = watchdogId
                    break

        if expiredWatchdogId != None:
            with self._watchdogLock:
                watchdog = self._watchdogs[expiredWatchdogId]
                self._logger.warning( "Watchdog %s not kicked in time" % ( watchdogId ) )
                if "callback" in watchdog:
                    callback = watchdog["callback"]
                    callback()

class ResourceMonitor( object ):
    __metaclass__ = Singleton

    __instance = None

    _logger = logging.getLogger( "aminopvr.ResourceMonitor" )

    def __init__( self ):
        self._dataIn = {
                        "multicast":  { "last": 0, "total": 0 },
                        "unicast":    { "last": 0, "total": 0 },
                        "epg":        { "last": 0, "total": 0 },
                        "content":    { "last": 0, "total": 0 },
                        "fileSystem": { "last": 0, "total": 0 }
                       }
        self._dataOut = {
                         "fileSystem": { "last": 0, "total": 0 }
                        }
        self._db = {
                    "select":     { "last": 0, "total": 0, "lastRows": 0, "totalRows": 0 },
                    "update":     { "last": 0, "total": 0, "lastRows": 0, "totalRows": 0 },
                    "insert":     { "last": 0, "total": 0, "lastRows": 0, "totalRows": 0 },
                    "delete":     { "last": 0, "total": 0, "lastRows": 0, "totalRows": 0 }
                   }

        now          = datetime.datetime.now()
        grabInterval = datetime.timedelta( minutes=10 )
        grabTime     = now + grabInterval

        self._logger.warning( "Starting ResourceMonitor timer @ %s with interval %s" % ( grabTime, grabInterval ) )

        self._timer = Timer( [ { "time": grabTime, "callback": self._timerCallback, "callbackArguments": None } ], pollInterval=10.0, recurrenceInterval=grabInterval )

        ResourceMonitor.__instance = self

    def stop( self ):
        self._logger.warning( "Stopping ResourceMonitor" )
        self._timer.stop()
        self._printTotals()

    @classmethod
    def report( cls, dataType, amount, direction ):
        # If cls.__instance is not set, it means nobody has initialized use yet
        # so, so maybe, we're not welcome. Just return
        if not cls.__instance:
            return
        instance = cls.__instance
        if direction == "db":
            cls.reportDb( dataType, amount, 0 )
        elif direction == "in":
            if instance._dataIn.has_key( dataType ):
                instance._dataIn[dataType]["total"] += amount
            else:
                instance._dataIn[dataType] = { "last": 0, "total": amount }
        elif direction == "out":
            if instance._dataOut.has_key( dataType ):
                instance._dataOut[dataType]["total"] += amount
            else:
                instance._dataOut[dataType] = { "last": 0, "total": amount }
        else:
            cls._logger.error( "ResourceMonitor.report: unknown direction=%s" % ( direction ) )

    @classmethod
    def reportDb( cls, dataType, amount, rows ):
        # If cls.__instance is not set, it means nobody has initialized use yet
        # so, so maybe, we're not welcome. Just return
        if not cls.__instance:
            return
        instance = cls.__instance

        if rows < 0:
            rows = 0

        if instance._db.has_key( dataType ):
            instance._db[dataType]["total"]     += amount
            instance._db[dataType]["totalRows"] += rows
        else:
            instance._db[dataType] = { "last": 0, "total": amount, "lastRows": 0, "totalRows": rows }

    def _timerCallback( self, event, arguments ):
        if event == Timer.TIME_TRIGGER_EVENT:
            self._logger.debug( "Time to display resource usage." )

    def _printTotals( self ):
        self._logger.warning( "Resource Monitor Totals" )
        self._logger.warning( "Data In:" )
        for dataType in self._dataIn.keys():
            self._logger.warning( "- %s: %d kb" % ( dataType, self._dataIn[dataType]["total"] / 1024 ) )
        self._logger.warning( "Data Out:" )
        for dataType in self._dataOut.keys():
            self._logger.warning( "- %s: %d kb" % ( dataType, self._dataOut[dataType]["total"] / 1024 ) )
        self._logger.warning( "Database:" )
        for dataType in self._db.keys():
            self._logger.warning( "- %s: %d (rows affected: %d)" % ( dataType, self._db[dataType]["total"], self._db[dataType]["totalRows"] ) )
