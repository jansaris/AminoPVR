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
from aminopvr.config import ConfigSectionAbstract, config
from aminopvr.multicast import MulticastSocket
import logging
import urllib2

class InputStreamProtocol( object ):
    MULTICAST = 1
    HTTP      = 2

class InputStreamConfig( ConfigSectionAbstract ):
    _section = "InputStreams"
    _options = {
                 "http_base_url": "http://localhost:4022/[protocol]/[ip]:[port]"
               }

    @property
    def httpBaseUrl( self ):
        return self._get( "http_base_url" )

inputStreamConfig = InputStreamConfig( config )

class InputStreamAbstract( object ):
    """
    InputStreamAbstract base class
    """
    _logger = logging.getLogger( "aminopvr.InputStreamAbstract" )

    def __init__( self ):
        self._logger.debug( "InputStreamAbstract.__init__()" )

    @classmethod
    def createInputStream( cls, protocol, url ):
        """
        Create correct instance of InputStreamAbstract derived class depending on 'protocol'

        @param protocol: type of protocol (e.g. multicast, http)
        @param url:      instance of 'channel.ChannelUrl'
        """
        if protocol == InputStreamProtocol.MULTICAST:
            return MulticastInputStream( url.ip, url.port )
        elif protocol == InputStreamProtocol.HTTP:
            return HttpInputStream( cls.getUrl( InputStreamProtocol.HTTP, url ) )
        return None

    @classmethod
    def getUrl( cls, protocol, url ):
        if protocol == InputStreamProtocol.HTTP:
            return HttpInputStream.getUrl( url )
        return None

class MulticastInputStream( InputStreamAbstract ):
    _logger = logging.getLogger( "aminopvr.MulticastInputStream" )

    def __init__( self, ip, port ):
        InputStreamAbstract.__init__( self )

        self._ip     = ip
        self._port   = port
        self._socket = None

    def open( self ):
        try:
            self._socket = MulticastSocket( self._port, True )
            self._socket.add( self._ip )
        except:
            self._logger.debug( "Cannot open multicast: %s:%i, filename: %s" % ( self._ip, self._port ) )
            return False
        return True

    def close( self ):
        self._socket.close()

    def read( self, length ):
        return self._socket.recv( length )

class HttpInputStream( InputStreamAbstract ):
    _logger = logging.getLogger( "aminopvr.HttpInputStream" )

    def __init__( self, url ):
        InputStreamAbstract.__init__( self )
        self._url     = url
        self._request = None

    def open( self ):
        self._logger.info( "HttpInputStream.open: url=%s" % ( self._url ) )
        try:
            self._request = urllib2.urlopen( self._url )
        except urllib2.HTTPError, e:
            self._logger.warning( "Cannot open url: %s" % ( self._url ) )
            self._logger.warning( "HTTP Error code: %d" % e.code )
            return False
        except urllib2.URLError, e:
            self._logger.warning( "Cannot open url: %s" % ( self._url ) )
            self._logger.warning( "URL Error reason: %s" % e.reason )
            return False
        except:
            self._logger.warning( "Cannot open url: %s" % ( self._url ) )
            return False
        return True

    def close( self ):
        self._request.close()

    def read( self, length ):
        return self._request.read( length )

    @classmethod
    def getUrl( cls, url ):
        if url.arguments == ";rtpskip=yes":
            protocol = "rtp"
        else:
            protocol = "udp"

        httpBaseUrl = inputStreamConfig.httpBaseUrl
        formatMap = {
                        "[protocol]": protocol,
                        "[ip]":       url.ip,
                        "[port]":     str( url.port )
                    }

        return reduce( lambda x, y: x.replace( y, formatMap[y] ), formatMap, httpBaseUrl )
