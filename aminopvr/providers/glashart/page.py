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
import logging

class PageSymbol( object ):
    _logger = logging.getLogger( 'aminopvr.providers.glashart.PageSymbol' )

    def __init__( self, key, value ):
        self._key   = unicode( key )
        self._value = unicode( value )

    def __hash__( self ):
        return ( hash( self._key ) )

    def __eq__( self, other ):
        return ( self._key   == other._key   and
                 self._value == other._value )

    def __ne__( self, other ):
        return not self.__eq__( other )

    def __str__( self ):
        return self._value

    @property
    def key( self ):
        return self._key

    @property
    def value( self ):
        return self._value

    @classmethod
    def getAllFromDb( cls, conn ):
        symbols = {}
        if conn:
            rows = conn.execute( "SELECT * FROM glashart_page_symbols" )
            for row in rows:
                symbols[unicode( row["key"] )] = PageSymbol( row["key"], row["value"] )

        return symbols

    @classmethod
    def getFromDb( cls, conn, key ):
        symbol = None
        if conn:
            row = conn.execute( "SELECT * FROM glashart_page_symbols WHERE key=?", ( key, ) )
            if row:
                symbol = PageSymbol( row[0]["key"], row[0]["value"] )

        return symbol

    def addToDb( self, conn ):
        if conn:
            symbol = self.getFromDb( conn, self._key )

            if symbol:
                if self != symbol:
                    conn.execute( "UPDATE glashart_page_symbols SET value=? WHERE key=?", ( self._value, self._key ) )
            else:
                conn.insert( "INSERT INTO glashart_page_symbols (key, value) VALUES (?, ?)", ( self._key, self._value ) )

    @classmethod
    def addAllDictToDb( cls, conn, symbols ):
        for key in symbols.keys():
            symbol = PageSymbol( key, symbols[key] )
            symbol.addToDb( conn )
