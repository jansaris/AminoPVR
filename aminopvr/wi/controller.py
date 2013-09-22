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
from Queue import Empty, Queue
from aminopvr.tools import Singleton
import threading

class Controller( object ):
    __metaclass__ = Singleton

    TYPE_CONTROLLER = 1
    TYPE_RENDERER   = 2

    def __init__( self ):
        self._listeners  = {}
        self._listenerId = 0
        self._lock       = threading.RLock()

    def addListener( self, ip, type ):  # @ReservedAssignment
        listenerId = -1
        with self._lock:
            for id_ in self._listeners:
                if ip == self._listeners[id_]["ip"] and type == self._listeners[id_]["type"]:
                    listenerId = id_
                    break
            if listenerId != -1:
                self.removeController( listenerId )

            listener   = { "ip": ip, "type": type, "queue": Queue() }
            listenerId = self._listenerId
            self._listeners[listenerId] = listener
            self._listenerId += 1
        return listenerId

    def removeController( self, id ):  # @ReservedAssignment
        with self._lock:
            if id in self._listeners:
                del self._listeners[id]

    def isListener( self, id ):  # @ReservedAssignment
        with self._lock:
            if id in self._listeners:
                return True
        return False

    def getListeners( self ):
        listeners = []
        with self._lock:
            for id_ in self._listeners:
                listeners.append( { "id": id_, "ip": self._listeners[id_]["ip"], "type": self._listeners[id_]["type"] } )
        return listeners

    def sendMessage( self, fromId, toIp, toType, message ):
        with self._lock:
            if fromId not in self._listeners:
                return False
        listener = self._getListener( toIp, toType )
        if listener:
            if "from" not in message:
                message["from"] = fromId
            listener["queue"].put( message )
            return True
        return False

    def sendMessageToId( self, fromId, toId, message ):
        with self._lock:
            if toId not in self._listeners:
                return False
        listener = self._listeners[toId]
        return self.sendMessage( fromId, listener["ip"], listener["type"], message )

    def getMessage( self, id, timeout=25.0 ):  # @ReservedAssignment
        listener = None
        with self._lock:
            if id in self._listeners:
                listener = self._listeners[id]
        if listener:
            try:
                message = listener["queue"].get( True, timeout )
            except Empty:
                return None
            return message
        return None

    def _getListener( self, ip, type ):  # @ReservedAssignment
        with self._lock:
            for id_ in self._listeners:
                if ip == self._listeners[id_]["ip"] and type == self._listeners[id_]["type"]:
                    return self._listeners[id_]
        return None
