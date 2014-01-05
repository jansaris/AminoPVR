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
import aminopvr
import errno
import getopt
import logging
import os
import signal
import sys
import threading
import time

class CustomFormatter( logging.Formatter ):
    width = 16

    def __init__( self, default ):
        self._default = default

    def format( self, record ):
        if len( record.name ) > self.width:
            record.name = record.name[-self.width:]
        return self._default.format( record )

def formatFactory( fmt, datefmt ):
    default = logging.Formatter( fmt, datefmt )
    return CustomFormatter( default )

formatter = CustomFormatter( logging.Formatter( "%(asctime)s <%(levelname).1s> %(name)16s[%(lineno)4d]: %(message)s", "%Y%m%d %H:%M:%S" ) )

fileHandler = logging.FileHandler( "AminoPVR.log" )
fileHandler.setLevel( logging.DEBUG )
fileHandler.setFormatter( formatter )

cherryPyFileHandler = logging.FileHandler( "AminoPVR.log" )
cherryPyFileHandler.setLevel( logging.WARNING )
cherryPyFileHandler.setFormatter( formatter )

logger = logging.getLogger( "aminopvr" )
logger.setLevel( logging.WARNING )
logger.addHandler( fileHandler )

cherryPyLogger = logging.getLogger( "cherrypy" )
cherryPyLogger.addHandler( cherryPyFileHandler )


signal.signal( signal.SIGINT,   aminopvr.signalHandler )
signal.signal( signal.SIGTERM,  aminopvr.signalHandler )
try:
    signal.signal( signal.SIGBREAK, aminopvr.signalHandler )
except:
    pass

def daemonize():
    """
    Fork off as a daemon
    """

    # pylint: disable=E1101
    # Make a non-session-leader child process
    try:
        pid = os.fork()  # @UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit( 0 )
    except OSError, e:
        raise RuntimeError( "1st fork failed: %s [%d]" % ( e.strerror, e.errno ) )

    os.setsid()  # @UndefinedVariable - only available in UNIX

    # Make sure I can read my own files and shut out others
    prev = os.umask( 0 )
    os.umask( prev and int( '077', 8 ) )

    # Make the child a session-leader by detaching from the terminal
    try:
        pid = os.fork()  # @UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit( 0 )
    except OSError, e:
        raise RuntimeError( "2nd fork failed: %s [%d]" % ( e.strerror, e.errno ) )

    dev_null = file( '/dev/null', 'r' )
    os.dup2( dev_null.fileno(), sys.stdin.fileno() )

    if aminopvr.const.CREATEPID:
        pid = str( os.getpid() )
        logger.warning( "Writing PID %s to %s" % ( pid, aminopvr.const.PIDFILE ) )
        file( aminopvr.const.PIDFILE, 'w' ).write( "%s\n" % pid )

def _stopDaemon():
    pid = int( file( aminopvr.const.PIDFILE, 'r' ).read() )
    logger.warning( "Killing pid: %d" % ( pid ) )
    try:
        os.kill( pid, signal.SIGTERM )  # @UndefinedVariable - only available in UNIX
    except OSError, e:
        raise RuntimeError( "Waiting for pid: %d failed: %s [%d]" % ( pid, e.strerror, e.errno ) )
    # Wait for process to finish by polling if it still exists.
    while 1:
        try:
            os.kill( pid, 0 )
        except OSError, e:
            if e.errno != errno.EPERM:
                break
        time.sleep( 0.1 )
    logger.warning( "Old daemon with pid: %d exited" % ( pid ) )

def main():
    aminopvr.const.DATA_ROOT = os.path.dirname( os.path.abspath( __file__ ) )

    # Rename the main thread
    threading.currentThread().name = "MAIN"

    consoleLogging = True
    stopDaemon     = False
    restartDaemon  = False
    forceStop      = False

    try:
        opts, args = getopt.getopt( sys.argv[1:], "qd", ['quiet', 'daemon', 'pidfile=', 'stop', 'restart', 'force'] )  # @UnusedVariable
    except getopt.GetoptError:
        print "Available Options: --quiet, --daemon, --pidfile, --stop, --restart"
        sys.exit()

    for o, a in opts:
        # For now we'll just silence the logging
        if o in ( '-q', '--quiet' ):
            consoleLogging = False

        if o in ( '--stop' ):
            if sys.platform == 'win32':
                print "Stop daemon not supported under Windows"
                sys.exit()
            else:
                stopDaemon = True

        if o in ( '--restart' ):
            if sys.platform == 'win32':
                print "Restart daemon not supported under Windows"
                sys.exit()
            else:
                restartDaemon = True

        if o in ( '--force' ):
            forceStop = True

        # Run as a daemon
        if o in ( '-d', '--daemon' ):
            if sys.platform == 'win32':
                print "Daemonize not supported under Windows, starting normally"
            else:
                consoleLogging = False
                aminopvr.const.DAEMON = True

    for o, a in opts:
        # Write a pidfile if requested
        if o in ( '--pidfile', ):
            aminopvr.const.PIDFILE = str( a )

            if stopDaemon or restartDaemon:
                # If the pidfile does not exist, AminoPVR may not be running, so exit
                if not os.path.exists( aminopvr.const.PIDFILE ):
                    sys.exit( "PID file '" + aminopvr.const.PIDFILE + "' does not exist. Exiting." )

                if restartDaemon and aminopvr.const.DAEMON:
                    aminopvr.const.CREATEPID = True
                else:
                    print "Not running in daemon mode. PID file creation disabled."
            else:
                # If the pidfile already exists, AminoPVR may still be running, so exit
                if os.path.exists( aminopvr.const.PIDFILE ):
                    sys.exit( "PID file '" + aminopvr.const.PIDFILE + "' already exists. Exiting." )

                # The pidfile is only useful in daemon mode, make sure we can write the file properly
                if aminopvr.const.DAEMON:
                    aminopvr.const.CREATEPID = True
                    try:
                        file( aminopvr.const.PIDFILE, 'w' ).write( "pid\n" )
                    except IOError, e:
                        raise SystemExit( "Unable to write PID file: %s [%d]" % ( e.strerror, e.errno ) )
                else:
                    print "Not running in daemon mode. PID file creation disabled."

    if stopDaemon or restartDaemon:
        if not forceStop and aminopvr.isRecordingActive():
            print "Cannot stop process while recording is active. Use --force to force stop."
            sys.exit()
        _stopDaemon()
        if stopDaemon:
            sys.exit()

    aminopvr.init()

    if consoleLogging:
        consoleHandler = logging.StreamHandler( sys.stdout )
        consoleHandler.setLevel( logging.INFO )
        consoleHandler.setFormatter( formatter )
        cherryPyConsoleHandler = logging.StreamHandler( sys.stdout )
        cherryPyConsoleHandler.setLevel( logging.WARNING )
        cherryPyConsoleHandler.setFormatter( formatter )

        logger.addHandler( consoleHandler )
        cherryPyLogger.addHandler( cherryPyConsoleHandler )

    if aminopvr.const.DAEMON:
        daemonize()

    # Use this PID for everything
    aminopvr.const.PID = os.getpid()

    aminopvr.aminoPVRProcess()

    try:
        while 1:
            time.sleep( 1.0 )
            pass
    except KeyboardInterrupt:
        logger.warning( "Clean exit" )

    sys.exit( 0 )

if __name__ == "__main__":
    main()
