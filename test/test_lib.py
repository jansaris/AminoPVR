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
import logging
import os.path
import sys
import unittest
from aminopvr import database, db, config


sys.path.append( os.path.abspath( '..' ) )
sys.path.append( os.path.abspath( '../lib' ) )


#=================
# test globals
#=================
TESTDIR        = os.path.abspath( '.' )
TESTDBNAME     = "aminopvr_test.db"
TESTCONFIGNAME = "aminopvr_test.conf"

#=================
# aminopvr globals
#=================
aminopvr.const.DATA_ROOT = os.path.abspath( '..' )

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

fileHandler = logging.FileHandler( "AminoPVR_test.log" )
fileHandler.setLevel( logging.DEBUG )
fileHandler.setFormatter( formatter )

logger = logging.getLogger( "aminopvr" )
logger.setLevel( logging.WARNING )
logger.addHandler( fileHandler )

#=================
# test classes
#=================
class AminoPVRTestDBCase( unittest.TestCase ):
    def setUp( self ):
        setUp_test_db()

    def tearDown( self ):
        tearDown_test_db()

class TestDBConnection( db.DBConnection, object ):

    def __init__( self, dbFileName=TESTDBNAME ):
        dbFileName = os.path.join( TESTDIR, dbFileName )
        super( TestDBConnection, self ).__init__( dbFileName )

class TestConfig( config.Config, object ):

    def __init__( self, configFileName=TESTCONFIGNAME ):
        configFileName = os.path.join( TESTDIR, configFileName )
        super( TestConfig, self ).__init__( configFileName )

# this will override the normal db connection
aminopvr.db.DBConnection = TestDBConnection
aminopvr.config.Config   = TestConfig


#=================
# test functions
#=================
def setUp_test_db():
    """
    upgrades the db to the latest version
    """
    # upgrading the db
    db.upgradeDatabase( db.DBConnection(), database.InitialSchema )
    # fix up any db problems
    db.sanityCheckDatabase( db.DBConnection(), database.MainSanityCheck )


def tearDown_test_db():
    """
    Deletes the test db
    """
    if os.path.exists( os.path.join( TESTDIR, TESTDBNAME ) ):
        os.remove( os.path.join( TESTDIR, TESTDBNAME ) )

def tearDown_test_config():
    """
    Deletes the test config
    """
    if os.path.exists( os.path.join( TESTDIR, TESTCONFIGNAME ) ):
        os.remove( os.path.join( TESTDIR, TESTCONFIGNAME ) )

def createChannel( cls, number, radio=False, inactive=False ):
    channel = cls( -1,
                   number,
                   "test_%i" % ( number ),
                   "Test Channel %i" % ( number ),
                   "Test Chan %i" % ( number ),
                   "logo.png",
                   "thumbnail.png",
                   radio,
                   inactive )
    return channel

def createChannelUrl( cls, type, scrambled=False ):
    ip   = "123.456.987.123"
    port = 1234
    if type == "hd":
        ip   = "321.789.654.321"
        port = 4321
    channelUrl = cls( type, "udp", ip, port, "args", scrambled )
    return channelUrl

tearDown_test_db()
tearDown_test_config()

if __name__ == '__main__':
    print "=================="
    print "Dont call this directly"
    print "=================="
    print "you might want to call"

    dirList = os.listdir( TESTDIR )
    for fname in dirList:
        if ( fname.find( "_test" ) > 0) and ( fname.find( "pyc" ) < 0 ):
            print "- " + fname

    print "=================="
    print "or just call all_tests.py"
