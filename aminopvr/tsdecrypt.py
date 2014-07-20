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
from aminopvr.config import ConfigSectionAbstract, Config
import logging
import os.path
import signal
import subprocess
import sys
import threading

TSDECRYPT = "tsdecrypt"

class TsDecryptConfig( ConfigSectionAbstract ):
    _section = "TsDecrypt"
    _options = {
                 "camd_protocol":   "NEWCAMD",
                 "camd_server":     "127.0.0.1:15050",
                 "camd_username":   "AminoPVR",
                 "camd_password":   "pass",
                 "camd_des_key":    "0102030405060708091011121314"
               }

def IsTsDecryptSupported():
    if sys.platform == 'win32':
        return False
    else:
        if not os.path.exists( os.path.join( const.DATA_ROOT, "bin", TSDECRYPT ) ):
            return False
    return True

class TsDecrypt( subprocess.Popen ):
    """
    Run tsdecrypt as a subprocess sending output to a logger.
    This class subclasses subprocess.Popen
    """

    _logger          = logging.getLogger( 'aminopvr.TsDecrypt' )
    _tsdecryptLogger = logging.getLogger( 'aminopvr.TsDecrypt.tsdecrypt' )

    def __init__( self, url, outputIp, outputPort ):
    
        self._logger.warning( "Starting tsdecrypt, output on %s:%d" % ( outputIp, outputPort ) )

        tsdecryptConfig = TsDecryptConfig( Config() )

        # -I 224.0.252.40:7080 -O 224.5.5.6:1234 -R -s 127.0.0.1:15051 -U tvheadend -P tvheadend -X 32
        args = []
        args.append( os.path.join( const.DATA_ROOT, "bin", TSDECRYPT ) )
        args.append( "--input" )
        args.append( "%s:%d" % ( url.ip, url.port ) )
        if url.arguments == ";rtpskip=yes":
            args.append( "--input-rtp" )
        args.append( "--output" )
        args.append( "%s:%d" % ( outputIp, outputPort ) )
        args.append( "--ecm-pid" )
        args.append( "32" )
        args.append( "--camd-proto" )
        args.append( tsdecryptConfig.camdProtocol )
        args.append( "--camd-server" )
        args.append( tsdecryptConfig.camdServer )
        args.append( "--camd-user" )
        args.append( tsdecryptConfig.camdUsername )
        args.append( "--camd-pass" )
        args.append( tsdecryptConfig.camdPassword )
        args.append( "--camd-des-key" )
        args.append( tsdecryptConfig.camdDesKey )

        self._logger.info( "Command line: %s" % ( ' '.join( args ) ) )

        # spawn the tsdecrypt process
        super( TsDecrypt, self ).__init__( args,
                                           cwd=os.path.abspath( os.path.join( const.DATA_ROOT, "bin" ) ),
                                           shell=False,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           bufsize=1,
                                           close_fds='posix' )

        if self.pid != 0:
            self._logger.warning( "tsdecrypt started with PID=%d" % ( self.pid ) )
        else:
            self._logger.error( "tsdecrypt not started" )

        # start stdout and stderr logging threads
        self._LogThread( self.stdout, self._tsdecryptLogger.info )
        self._LogThread( self.stderr, self._tsdecryptLogger.info )

    def terminate( self ):
        if self.pid != 0:
            self._logger.warning( "Stopping tsdecrypt" )
            self.send_signal( signal.SIGTERM )
            self.wait()
            self._logger.warning( "tsdecrypt stopped" )
            self.pid = 0

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
