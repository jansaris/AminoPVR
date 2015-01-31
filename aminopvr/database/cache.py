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
from aminopvr.tools import Singleton
import logging
import threading

class Cache( object ):

    __metaclass__ = Singleton

    __cachableObjectClasses = [ "channels", "epg_ids", "genres", "old_recordings", "pending_channels",
                                "persons", "recording_programs", "recordings", "schedules" ]

    _logger = logging.getLogger( "aminopvr.db.Cache" )
    _lock   = threading.Lock()

    def __init__( self ):
        with self._lock:
            self._cache = {}

    def cache( self, objectClass, itemId, item ):
        with self._lock:
            if objectClass in self.__cachableObjectClasses:
                if not objectClass in self._cache:
                    self._cache[objectClass] = {}
                self._cache[objectClass][itemId] = item

    def get( self, objectClass, itemId ):
        item = None
        with self._lock:
            if objectClass in self.__cachableObjectClasses:
                if objectClass in self._cache:
                    if itemId in self._cache[objectClass]:
                        item = self._cache[objectClass][itemId]
        return item

    def purge( self, objectClass=None, itemId=None ):
        with self._lock:
            if objectClass == None:
                self._cache = {}
            else:
                if objectClass in self.__cachableObjectClasses:
                    if objectClass in self._cache:
                        if itemId == None:
                            del self._cache[objectClass]
                        else:
                            if itemId in self._cache[objectClass]:
                                del self._cache[objectClass][itemId]
