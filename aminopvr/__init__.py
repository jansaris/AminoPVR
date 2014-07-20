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
from aminopvr.config import Config, GeneralConfig, DebugConfig
from aminopvr.db import DBConnection
from aminopvr.recorder import Recorder
from aminopvr.recording import Recording
from aminopvr.resource_monitor import ResourceMonitor
from aminopvr.rtsp_server import RtspServer
from aminopvr.scheduler import Scheduler
from aminopvr.timer import Timer
from aminopvr.wi import initWebserver, stopWebserver
import datetime
import logging
import os
import sys
import time
import traceback

logger          = logging.getLogger( "aminopvr" )

resourceMonitor = None
recorder        = None
scheduler       = None
epgGrabber      = None
contentProvider = None
vcasProvider    = None
rtspServer      = None

def init():
    debugConfig = DebugConfig( Config() )

    for debugLogger in debugConfig.logger.keys():
        loggerInst = logging.getLogger( debugLogger )
        if debugConfig.logger[debugLogger].lower() == "debug":
            loggerInst.setLevel( logging.DEBUG )
        elif debugConfig.logger[debugLogger].lower() == "info":
            loggerInst.setLevel( logging.INFO )
        elif debugConfig.logger[debugLogger].lower() == "warning":
            loggerInst.setLevel( logging.WARNING )
        elif debugConfig.logger[debugLogger].lower() == "error":
            loggerInst.setLevel( logging.ERROR )
        elif debugConfig.logger[debugLogger].lower() == "critical":
            loggerInst.setLevel( logging.CRITICAL )
        logger.warning( "Configured logger '%s' at level '%s'" % ( debugLogger, debugConfig.logger[debugLogger] ) )

#def test( eventType, params ):
#    logger.warning( "test" )

def signalHandler( signalNumber=None, frame=None ):
    if type( signalNumber ) != type( None ):
        logger.warning( "Signal %i caught, exiting..." % int( signalNumber ) )
        shutdown()

def shutdown():
    logger.warning( "Let's stop everything before we exit" )

    global epgGrabber, contentProvider, vcasProvider, recorder, scheduler, resourceMonitor

    stopRtspServer()
    if epgGrabber:
        epgGrabber.stop()
    if contentProvider:
        contentProvider.stop()
    if vcasProvider:
        vcasProvider.stop()
    if recorder:
        recorder.stopAllRecordings()
    if scheduler:
        scheduler.stop()
    if resourceMonitor:
        resourceMonitor.stop()
    stopWebserver()
    logger.warning( "Everything has stopped, now exit" )
    logging.shutdown()
    # Remove PID file if created
    if const.CREATEPID and os.path.exists( const.PIDFILE ):
        os.unlink( const.PIDFILE )
    os._exit( 0 )

def startRtspServer():
    global rtspServer

    rtspServer = RtspServer()

def stopRtspServer():
    if rtspServer != None:
        rtspServer.terminate()

def isRecordingActive():
    conn = DBConnection()
    unfinishedRecordings = Recording.getAllUnfinishedFromDb( conn )
    return len( unfinishedRecordings ) > 0

def aminoPVRProcess():
    logger.debug( 'aminoPVRProcess' )

    global epgGrabber, contentProvider, vcasProvider, recorder, scheduler, resourceMonitor

    generalConfig   = GeneralConfig( Config() )
    resourceMonitor = ResourceMonitor()
    recorder        = Recorder()
    scheduler       = Scheduler()
    startRtspServer()

    if generalConfig.provider == "glashart":
        import providers.glashart as provider
        provider.RegisterProvider()

    try:
        initWebserver( generalConfig.serverPort )
    except IOError:
        logger.error( u"Unable to start web server, is something else running on port %d?" % ( generalConfig.serverPort ) )
        sys.exit()

    scheduler.start()
    scheduler.requestReschedule()

    recorder.start()

    epgGrabber = provider.EpgProvider()
    epgGrabber.start()
#    epgGrabber.requestEpgUpdate()
    contentProvider = provider.ContentProvider()
    contentProvider.start()
#    contentProvider.requestContentUpdate()
    vcasProvider = provider.VcasProvider()
    vcasProvider.start()

#    from aminopvr.channel import ChannelUrl
#    from aminopvr.input_stream import InputStreamAbstract, InputStreamProtocol
    
#    url = ChannelUrl( "hd", "udp", "224.1.3.1", 12110, "", 0 )
#    stream = InputStreamAbstract.createInputStream( InputStreamProtocol.HTTP, url )
#    count = 0
#    if stream.open():
#        while count < 4:
#            data = stream.read( 160 * 1024 )
#            if data:
#                logger.warning( "read %d data" % ( len( data ) ) )
#            else:
#                logger.warning( "timeout" )
#            count += 1
#        stream.close()
