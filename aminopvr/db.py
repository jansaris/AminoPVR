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
from aminopvr.tools import ResourceMonitor
import logging
import os
import sqlite3
import threading
import time
import unicodedata

lock = threading.Lock()

def _like( mask, value, escape=None ):
    value = unicodedata.normalize( "NFKD", value ).encode( "ASCII", "ignore" )
    return mask[1:-1].lower() in value.lower()

class DBConnection:
    _logger = logging.getLogger( "aminopvr.db" )

    def __init__( self, filename="aminopvr.db" ):
        self._filename           = filename
        self._conn               = sqlite3.connect( DBConnection.dbFilename( filename ), 20 )
        self._cursor             = self._conn.cursor()
        self._cursor.row_factory = sqlite3.Row
        self._conn.create_function( "LIKE", 2, _like )
        self._conn.create_function( "LIKE", 3, _like )

    def execute( self, query, args=None ):
        if query == None:
            return
        with lock:
            sqlResult = None
            attempt   = 0
            while attempt < 5:
                try:
                    if args == None:
                        self._logger.debug( "%s: %s" % ( self._filename, query ) )
                        sqlResult = self._cursor.execute( query )
                    else:
                        self._logger.debug( "%s: %s with args %s" % ( self._filename, query, args ) )
                        sqlResult = self._cursor.execute( query, args )
                    self._conn.commit()
                    if query.lower().startswith( "select" ):
                        sqlResult = sqlResult.fetchall()
                        ResourceMonitor.reportDb( "select", 1, self._cursor.rowcount )
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
                        raise
                except sqlite3.DatabaseError, e:
                    self._logger.error( "Fatal error executing query: %s" % ( e.message ) )
                    raise

            return sqlResult

    def insert( self, query, args=None ):
        self.execute( query, args )
        ResourceMonitor.reportDb( "insert", 1, self._cursor.rowcount )
        return self._cursor.lastrowid

    @staticmethod
    def dbFilename( filename ):
        return os.path.join( DATA_ROOT, filename )
