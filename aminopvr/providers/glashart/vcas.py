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
from aminopvr.config import Config
from aminopvr.providers.glashart.config import GlashartConfig
from aminopvr.tools import parseTimedetlaString
import logging
import os.path
import signal
import subprocess
import sys
import threading

class VcasProvider( subprocess.Popen ):
    """
    Run vmcam as a subprocess sending output to a logger.
    This class subclasses subprocess.Popen
    """

    _logger      = logging.getLogger( 'aminopvr.VcasProvider' )
    _vmcamLogger = logging.getLogger( 'aminopvr.VcasProvider.vmcam' )

    def __init__( self ):
    
        vmcamServer = "vmcam"
        if sys.platform == 'win32':
            vmcamServer = ""

        glashartConfig = GlashartConfig( Config() )
        updateInterval = parseTimedetlaString( glashartConfig.vcasUpdateInterval )

        self._logger.warning( "Starting VCAS VMCAM server with interval %s" % ( updateInterval ) )

        self.pid = 0
        if vmcamServer != "":
            vmcamServerPath = os.path.join( const.DATA_ROOT, "bin", vmcamServer )

            #-e ./etc/ -c ../../Verimatrix.ini -t 86400 -keyblockonly
            args = []
            args.append( vmcamServerPath )
            args.append( "-e" )
            args.append( "./etc/" )
            args.append( "-c" )
            args.append( glashartConfig.vcasIniFile )
            args.append( "-t" )
            args.append( "%d" % ( updateInterval.total_seconds() ) )
            args.append( "-keyblockonly" )

            self._logger.info( "Command line: %s" % ( ' '.join( args ) ) )

            if os.path.isfile( vmcamServerPath ) and os.access( vmcamServerPath, os.X_OK ):
                # spawn the vmcam server process
                super( VcasProvider, self ).__init__( args,
                                                      cwd=os.path.abspath( os.path.join( const.DATA_ROOT, "bin" ) ),
                                                      shell=False,
                                                      stdout=subprocess.PIPE,
                                                      stderr=subprocess.PIPE,
                                                      bufsize=1,
                                                      close_fds='posix' )

                if self.pid != 0:
                    self._logger.warning( "VMCAM server started with PID=%d" % ( self.pid ) )
                else:
                    self._logger.error( "VMCAM server not started" )

                # start stdout and stderr logging threads
                self._LogThread( self.stdout, self._vmcamLogger.debug )
                self._LogThread( self.stderr, self._vmcamLogger.info )
            else:
                self._logger.warning( "VMCAM server executable %s does not exist or is not an executable." % ( vmcamServerPath ) )

    def terminate( self ):
        if self.pid != 0:
            self._logger.warning( "Stopping VMCAM server" )
            self.send_signal( signal.SIGTERM )
            self.wait()
            self._logger.warning( "VMCAM server stopped" )

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

def main():
    sys.stderr.write( "main()\n" );

# allow this to be a module
if __name__ == '__main__':
    main()
