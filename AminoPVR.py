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
from aminopvr import aminoPVRProcess
import logging.config
import sys

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
    logging.config.fileConfig( 'logging.conf', disable_existing_loggers=False )

    aminoPVRProcess()

    sys.exit( 0 )

if __name__ == "__main__":
    main()
