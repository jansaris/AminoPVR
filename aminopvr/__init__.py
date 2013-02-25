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
from aminopvr.config import config, GeneralConfig
from aminopvr.recorder import Recorder
from aminopvr.scheduler import Scheduler
from aminopvr.timer import Timer
from aminopvr.wi import initWebserver, stopWebserver
import datetime
import logging
import os
import time

logger          = logging.getLogger( "aminopvr" )

generalConfig   = GeneralConfig( config )
recorder        = Recorder()
scheduler       = Scheduler()
epgGrabber      = None
contentProvider = None

if generalConfig.provider == "glashart":
    import providers.glashart as provider
    provider.RegisterProvider()

#def test( eventType, params ):
#    logger.warning( "test" )

def signalHandler( signum=None, frame=None ):
    if type( signum ) != type( None ):
        logger.warning( "Signal %i caught, exiting..." % int( signum ) )
        shutdown()

def shutdown():
    logger.warning( "Let's stop everything before we exit" )
    if epgGrabber:
        epgGrabber.stop()
    if contentProvider:
        contentProvider.stop()
    recorder.stopAllRecordings()
    scheduler.stop()
    stopWebserver()
    logger.warning( "Everything has stopped, now exit" )
    os._exit( 0 )

def aminoPVRProcess():
    logger.debug( 'aminoPVRProcess' )

    initWebserver( generalConfig.serverPort )

    scheduler.start()

    global epgGrabber, contentProvider

    epgGrabber = provider.EpgProvider()
    epgGrabber.start()
#    epgGrabber.requestEpgUpdate()
    contentProvider = provider.ContentProvider()
    contentProvider.start()
    contentProvider.requestContentUpdate()
#    testTimer = Timer( [ { "time": datetime.datetime.now(), "callback": test, "callbackArguments": None } ], recurrenceInterval=datetime.timedelta( minutes=1 ) )
#    provider.epgGrabber()
#    recordingId = recorder.startRecording( '224.1.3.1:1234', 'http', 'test.ts' )
#    time.sleep( 60.0 )
#    recorder.stopRecording( recordingId )
