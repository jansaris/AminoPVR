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
from aminopvr.const import DATA_ROOT
from aminopvr.resource_monitor import ResourceMonitor
from aminopvr.tools import printTraceback
import logging
import os
import re
import sqlite3
import threading
import time
import unicodedata

_logger = logging.getLogger( "aminopvr.db" )

def _like( mask, value, escape=None ):
    value = unicodedata.normalize( "NFKD", value ).encode( "ASCII", "ignore" )
    return mask[1:-1].lower() in value.lower()

class DBConnection( object ):

    _logger = logging.getLogger( "aminopvr.db.DBConnection" )
    _lock   = threading.Lock()

    def __init__( self, filename="aminopvr.db" ):
        self._filename      = filename
        self._delayCommit   = False
        with self._lock:
            self._conn               = sqlite3.connect( self._dbFilename( filename ), 20 )
            self._cursor             = self._conn.cursor()
            self._cursor.row_factory = sqlite3.Row
            self._conn.create_function( "LIKE", 2, _like )
            self._conn.create_function( "LIKE", 3, _like )

    def __del__( self ):
        if self._conn:
            if self._delayCommit:
                self._conn.commit()
            self._conn.close()

    def delayCommit( self, enable ):
        if not enable and self._delayCommit:
            if self._conn:
                self._conn.commit()
        self._delayCommit = enable

    def execute( self, query, args=None, logger=None ):
        if query == None:
            return
        with self._lock:
            sqlResult = None
            attempt   = 0
            while attempt < 5:
                try:
                    if args == None:
                        sqlResult = self._cursor.execute( query )
                    else:
                        sqlResult = self._cursor.execute( query, args )
                    if logger:
                        logger.debug( "Executing query: %s with args=%r" % ( query, args ) )
                    if not self._delayCommit and not query.lower().startswith( "select" ):
                        self._conn.commit()
                    if query.lower().startswith( "select" ):
                        sqlResult = sqlResult.fetchall()
                        ResourceMonitor.reportDb( "select", 1, len( sqlResult ) )
                    elif query.lower().startswith( "update" ):
                        ResourceMonitor.reportDb( "update", 1, self._cursor.rowcount )
                    elif query.lower().startswith( "delete" ):
                        ResourceMonitor.reportDb( "delete", 1, self._cursor.rowcount )
                    break
                except sqlite3.OperationalError, e:
                    if "unable to open database file" in e.message or "database is locked" in e.message:
                        self._logger.warning( "DB error: %s" % ( e.message ) )
                        attempt += 1
                        time.sleep( 1 )
                    else:
                        self._logger.error( "DB error: %s" % ( e.message ) )
                        printTraceback()
                        raise
                except sqlite3.DatabaseError, e:
                    self._logger.error( "Fatal error executing query: %s" % ( e.message ) )
                    printTraceback()
                    raise

            return sqlResult

    def insert( self, query, args=None ):
        self.execute( query, args )
        ResourceMonitor.reportDb( "insert", 1, self._cursor.rowcount )
        return self._cursor.lastrowid

    @classmethod
    def _dbFilename( cls, filename ):
        return os.path.join( DATA_ROOT, filename )

def sanityCheckDatabase( connection, sanityCheck ):
    sanityCheck( connection ).check()

class DbSanityCheck( object ):
    def __init__( self, connection ):
        self.connection = connection

    def check( self ):
        pass

# ===============
# = Upgrade API =
# ===============

def upgradeDatabase( connection, schema ):
    _logger.warning( "Checking database structure..." )
    _processUpgrade( connection, schema )

def prettyName( str_ ):
    return ' '.join( [ x.group() for x in re.finditer( "([A-Z])([a-z0-9]+)", str_ ) ] )

def _processUpgrade( connection, upgradeClass ):
    instance = upgradeClass( connection )
    _logger.debug( "Checking %s database upgrade" % ( prettyName( upgradeClass.__name__ ) ) )
    if not instance.test():
        _logger.warning( "Database upgrade required: %s" % ( prettyName( upgradeClass.__name__ ) ) )
        try:
            instance.execute()
        except sqlite3.DatabaseError, e:
            print "Error in %s: %s" % ( upgradeClass.__name__, e )
            raise
        _logger.debug( "%s upgrade completed" % ( upgradeClass.__name__ ) )
    else:
        _logger.debug( "%s upgrade not required" % ( upgradeClass.__name__ ) )

    for upgradeSubClass in upgradeClass.__subclasses__():
        _processUpgrade( connection, upgradeSubClass )

# Base migration class. All future DB changes should be subclassed from this class
class SchemaUpgrade( object ):
    def __init__( self, connection ):
        self.connection = connection

    def hasTable( self, tableName ):
        return len( self.connection.execute( "SELECT 1 FROM sqlite_master WHERE name = ?;", ( tableName, ) ) ) > 0

    def hasColumn( self, tableName, column ):
        return column in self.connection.tableInfo( tableName )

    def addColumn( self, table, column, type="NUMERIC", default=0 ):  # @ReservedAssignment
        self.connection.execute( "ALTER TABLE %s ADD %s %s" % ( table, column, type ) )
        self.connection.execute( "UPDATE %s SET %s = ?" % ( table, column ), ( default, ) )

    def checkDbVersion( self ):
        try:
            result = self.connection.execute( "SELECT db_version FROM db_version" )
        except:
            _logger.error( "checkDbVersion: db_version table not found!" )
            printTraceback()
            return 0

        if result:
            return int( result[0]["db_version"] )
        else:
            return 0

    def incDbVersion( self ):
        curVersion = self.checkDbVersion()
        self.connection.execute( "UPDATE db_version SET db_version = ?", [curVersion + 1] )
        return curVersion + 1
