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
from urllib2 import Request, urlopen, HTTPError, URLError
import aminopvr
import ctypes
import datetime
import logging
import os
import platform
import re
import threading
import time
import traceback
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

def getTimestamp( t=None ):
    if not t:
        t = time.localtime()
    if isinstance( t, datetime.datetime ):
        t = t.timetuple()
    return int( time.mktime( t ) )

_timedeltaRegex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')

def parseTimedetlaString( timeString ):
    parts = _timedeltaRegex.match( timeString )
    if not parts:
        return
    parts      = parts.groupdict()
    timeParams = {}
    for ( name, param ) in parts.iteritems():
        if param:
            timeParams[name] = int( param )
    return datetime.timedelta( **timeParams )

def getFreeTotalSpaceMb( path ):
    """ Return folder/drive free space (in bytes)
    """
    path = os.path.abspath( path )
    if platform.system() == 'Windows':
        freeBytes  = ctypes.c_ulonglong( 0 )
        totalBytes = ctypes.c_ulonglong( 0 )
        ctypes.windll.kernel32.GetDiskFreeSpaceExW( ctypes.c_wchar_p( path ), None, ctypes.pointer( totalBytes ), ctypes.pointer( freeBytes ) ) # @UndefinedVariable - only available in Windows
        return ( freeBytes.value / 1024 / 1024, totalBytes.value / 1024 / 1024 )
    else:
        st = os.statvfs( path ) # @UndefinedVariable - only available in UNIX
        return ( st.f_bavail * st.f_frsize / 1024 / 1024, st.f_blocks * st.f_frsize / 1024 / 1024 )

def printTraceback():
    logger = logging.getLogger( "aminopvr.trace" )
    logger.debug( traceback.format_exc() )
