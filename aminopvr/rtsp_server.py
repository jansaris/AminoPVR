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
from aminopvr import const
from aminopvr.config import GeneralConfig, Config
import logging
import os.path
import signal
import subprocess
import sys
import threading

class RtspServer( subprocess.Popen ):
    """
    Run live555MediaServer as a subprocess sending output to a logger.
    This class subclasses subprocess.Popen
    """

    _logger        = logging.getLogger( 'aminopvr.RtspServer' )
    _live555Logger = logging.getLogger( 'aminopvr.RtspServer.live555' )

    def __init__( self ):
    
        self._logger.warning( "Starting RTSP server" )

        rtspServer = "live555MediaServer"
        if sys.platform == 'win32':
            rtspServer = "live555MediaServer.exe"

        generalConfig = GeneralConfig( Config() )

        self.pid = 0

        rtspServerPath = os.path.join( const.DATA_ROOT, "bin", rtspServer )
        if os.path.isfile( rtspServerPath ) and os.access( rtspServerPath, os.X_OK ):
            # spawn the rtsp server process
            if sys.platform == 'win32':
                super( RtspServer, self ).__init__( rtspServerPath,
                                                    cwd=os.path.abspath( generalConfig.recordingsPath ),
                                                    shell=False,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    bufsize=1 )
            else:
                super( RtspServer, self ).__init__( rtspServerPath,
                                                    cwd=os.path.abspath( generalConfig.recordingsPath ),
                                                    shell=False,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    bufsize=1,
                                                    close_fds='posix' )

            if self.pid != 0:
                self._logger.warning( "RTSP server started with PID=%d" % ( self.pid ) )
            else:
                self._logger.error( "RTSP server not started" )
    
            # start stdout and stderr logging threads
            self._LogThread( self.stdout, self._live555Logger.debug )
            self._LogThread( self.stderr, self._live555Logger.info )
        else:
            self._logger.warning( "RTSP server executable %s does not exist or is not an executable." % ( rtspServerPath ) )

    def shutdown( self ):
        if self.pid != 0:
            self._logger.warning( "Stopping RTSP server" )
            self.send_signal( signal.SIGTERM )
            self.wait()
            self._logger.warning( "RTSP server stopped" )

    def _LogThread( self, pipe, logger ):
        """
        Start a thread logging output from pipe
        """

        # thread function to log subprocess output
        def _LogOutput(out, logger):
            for line in iter( out.readline, b'' ):
                logger( line.rstrip( '\n' ) )

        # start thread
        t = threading.Thread( target=_LogOutput, args=( pipe, logger ) )
        t.daemon = True # thread dies with the program
        t.start()
