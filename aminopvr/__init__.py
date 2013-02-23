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
from aminopvr.wi import initWebserver
import datetime
import logging
import os
import time

logger        = logging.getLogger( "aminopvr" )

generalConfig = GeneralConfig( config )
recorder      = Recorder()
scheduler     = Scheduler()

#def test( eventType, params ):
#    logger.warning( "test" )

def aminoPVRProcess():
    logger.debug( 'aminoPVRProcess' )

    if generalConfig.provider == "glashart":
        import providers.glashart as provider
        provider.RegisterProvider()

    initWebserver()

    scheduler.start()

    epgGrabber = provider.EpgProvider()
#    epgGrabber.requestEpgUpdate()
    contentProvider = provider.ContentProvider()
#    testTimer = Timer( [ { "time": datetime.datetime.now(), "callback": test, "callbackArguments": None } ], recurrenceInterval=datetime.timedelta( minutes=1 ) )
#    testTimer.start()
#    provider.epgGrabber()
#    recordingId = recorder.startRecording( '224.1.3.1:1234', 'http', 'test.ts' )
#    time.sleep( 60.0 )
#    recorder.stopRecording( recordingId )
