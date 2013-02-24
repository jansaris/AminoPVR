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
import logging.config
import os
import signal
import sys

logging.config.fileConfig( 'logging.conf', disable_existing_loggers=True )


signal.signal( signal.SIGINT,   aminopvr.signalHandler )
signal.signal( signal.SIGTERM,  aminopvr.signalHandler )
try:
    signal.signal( signal.SIGBREAK, aminopvr.signalHandler )
except:
    pass

def main():
#    logger = logging.getLogger( "AminoPVR" )
#    logger.setLevel( logging.DEBUG )
#    ch = logging.StreamHandler()
#    ch.setLevel( logging.DEBUG )
#
#    formatter = logging.Formatter( '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S' )
#    ch.setFormatter( formatter )
#
#    logger.addHandler( ch )

#    logging.basicConfig( format='%(asctime)s %(levelname)s:$(message)s',
#                         datefmt='%Y%m%d %H:%M:%S',
#                         level=logging.DEBUG )

    aminopvr.const.DATA_ROOT = os.path.dirname( os.path.abspath( __file__ ) )
    aminopvr.aminoPVRProcess()

    logger = logging.getLogger( "aminopvr" )
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        logger.warning( "Clean exit" )

    sys.exit( 0 )

if __name__ == "__main__":
    main()
