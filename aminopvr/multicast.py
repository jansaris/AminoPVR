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
import socket
import struct

class MulticastSocket( socket.socket ):
    """
    Multicast socket implementation to enable handling of IGMP streams
    """
    def __init__( self, localPort, reuse=False ):
        socket.socket.__init__( self, socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP )
        if ( reuse ):
            self.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
            if hasattr( socket, "SO_REUSEPORT" ):
                self.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEPORT, 1 )
        self.bind( ('', localPort) )

    def add( self, addr ):
        mreq = struct.pack( "=4sl", socket.inet_aton( addr ), socket.INADDR_ANY )
        self.setsockopt( socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq )
