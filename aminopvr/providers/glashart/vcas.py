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
from aminopvr.config import Config
from aminopvr.providers.glashart.config import GlashartConfig
from aminopvr.timer import Timer
from aminopvr.tools import Singleton, parseTimedetlaString, printTraceback
#import lib.VCASpy.vcas.connector as vcas.connector
from lib.VCASpy import VcasConnector
import datetime
import logging
import threading
import time
import sys

class VcasProvider( threading.Thread ):
    __metaclass__ = Singleton

    _logger       = logging.getLogger( "aminopvr.providers.glashart.VcasProvider" )

    def __init__( self ):
        threading.Thread.__init__( self )

        self._logger.debug( "VcasProvider" )

        self._glashartConfig = GlashartConfig( Config() )

        now            = datetime.datetime.now()
        updateInterval = parseTimedetlaString( self._glashartConfig.vcasUpdateInterval )
        updateTime     = now + updateInterval

        self._logger.warning( "Starting VCAS update timer with interval %s" % ( updateInterval ) )

        self._running = True
        self._event   = threading.Event()
        self._event.clear()

        self._timer = Timer( [ { "time": updateTime, "callback": self._timerCallback, "callbackArguments": None } ],
                             pollInterval       = 10.0,
                             recurrenceInterval = updateInterval )

    def requestVcasUpdate( self, wait=False ):
        if not self._event.isSet():
            self._event.set()
            if wait:
                while self._event.isSet():
                    time.sleep( 1.0 )
            return True
        else:
            self._logger.warning( "Vcas update in progress: skipping request" )
            return False

    def stop( self ):
        self._logger.warning( "Stopping VcasProvider" )
        self._timer.stop()
        self._running = False
        self._event.set()
        self.join()

    def run( self ):
        while self._running:
            self._event.wait()
            if self._running:
                try:
                    self._update()
                except:
                    self._logger.error( "run: unexcepted error: %s" % ( sys.exc_info()[0] ) )
                    printTraceback()
                # Request a reschedule
            self._event.clear()

    def _timerCallback( self, event, arguments ):
        if event == Timer.TIME_TRIGGER_EVENT:
            self._logger.info( "Time to update VCAS." )
            self.requestVcasUpdate( True )

    def _update( self ):
        self._logger.debug( "VcasProvider._update" )

        self._logger.info( "Updating VCAS channel list." )

        VcasConnector( self._glashartConfig.vcasIniFile,
                       self._glashartConfig.vcasInterface,
                       self._glashartConfig.vcasJsonFile,
                       self._glashartConfig.vcasConstCwFile,
                       self._glashartConfig.vcasMacAddress )

def main():
    sys.stderr.write( "main()\n" );

# allow this to be a module
if __name__ == '__main__':
    main()
