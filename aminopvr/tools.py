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
from aminopvr.const import GLOBAL_TIMEOUT, USER_AGENT
from aminopvr.timer import Timer
from urllib2 import Request, urlopen, HTTPError, URLError
import aminopvr
import datetime
import logging
import threading
import urllib

class Singleton( type ):
    _instances = {}
    def __call__( self, *args, **kwargs ):
        if self not in self._instances:
            self._instances[self] = super( Singleton, self ).__call__( *args, **kwargs )
        return self._instances[self]

class fetchURL( threading.Thread ):

    _url      = ""
    _filename = ""
    _method   = "GET"
    _args     = {}

    result    = None
    code      = 500
    mimeinfo  = None

    """
    A simple thread to fetch a url with a timeout
    """
    def __init__( self, url, filename = None, method="GET", args={} ):
        threading.Thread.__init__( self )
        self._url        = url
        self._filename   = filename
        self._method     = method
        self._args       = args

        self.result      = None
        self.code        = 500
        self.mimeinfo    = None

    def run( self ):
        self.result, self.code, self.mimeinfo = self.getPageInternal()

    def getPageInternal( self ):
        """
        Retrieves the url and returns a string with the contents.
        Optionally, returns None if processing takes longer than
        the specified number of timeout seconds.
        """
        txtdata    = None
        if self._method == "POST":
            txtdata = urllib.urlencode( self._args )
        txtheaders = { 'Keep-Alive' : '300',
                       'User-Agent' : USER_AGENT }
        try:
            rurl   = Request( self._url, txtdata, txtheaders )
            fp     = urlopen( rurl )
    
            if self._filename != None:
                output = open( self._filename, 'wb' )
                output.write( fp.read() )
                output.close()
                return ( self._filename, 200, fp.info() )
            else:
                lines = fp.readlines()
                page  = "".join( lines )
                return ( page, 200, fp.info() )

        except HTTPError, e:
            aminopvr.logger.warning( 'Cannot open url: %s, filename: %s' % ( self._url, self._filename ) )
            aminopvr.logger.warning( 'HTTP Error code: %d' % e.code )
            return ( None, e.code, None )
        except URLError, e:
            aminopvr.logger.warning( 'Cannot open url: %s, filename: %s' % ( self._url, self._filename ) )
            aminopvr.logger.warning( 'URL Error reason: %s' % e.reason )
            return ( None, 500, None )
        except:
            aminopvr.logger.warning( 'Cannot open url: %s, filename: %s' % ( self._url, self._filename ) )
            return ( None, 500, None )

def getPage( url, filename = None, method="GET", args={} ):
    """
    Wrapper around get_page_internal to catch the
    timeout exception
    """
    try: 
        fu = fetchURL( url, filename, method, args )
        fu.start()
        fu.join( GLOBAL_TIMEOUT )

        return ( fu.result, fu.code, fu.mimeinfo )
    except:
        aminopvr.logger.debug( 'getPage timed out on (>%s s): %s' % ( GLOBAL_TIMEOUT, url ) )
        return ( None, 500, None )

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
            if instance._dateOut.has_key( dataType ):
                instance._dateOut[dataType]["total"] += amount
            else:
                instance._dateOut[dataType] = { "last": 0, "total": amount }
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
