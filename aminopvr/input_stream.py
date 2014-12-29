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
from aminopvr.config import Config, ConfigSectionAbstract, defaultConfig
from aminopvr.multicast import MulticastSocket
from aminopvr.tsdecrypt import TsDecrypt
from lib import httpplus
import logging
import socket
import time
import urlparse
#import urllib2

class InputStreamProtocol( object ):
    MULTICAST   = 1
    HTTP        = 2
    TSDECRYPT   = 3
    MOCK        = 0xff

class InputStreamConfig( ConfigSectionAbstract ):
    _section = "InputStreams"
    _options = {
                 "http_base_url":       "http://localhost:4022/[protocol]/[ip]:[port]",
                 "tsdecrypt_base_port": 1234
               }

class InputStreamAbstract( object ):
    """
    InputStreamAbstract base class
    """
    def __init__( self ):
        pass

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
            return HttpInputStream( url )
        elif protocol == InputStreamProtocol.TSDECRYPT:
            return TsDecryptInputStream( url )
        elif protocol == InputStreamProtocol.MOCK:
            return MockInputStream( url.ip, url.port )
        return None

    @classmethod
    def getUrl( cls, protocol, url ):
        if protocol == InputStreamProtocol.HTTP:
            return HttpInputStream.getUrl( url )
        elif protocol == InputStreamProtocol.MULTICAST:
            return MulticastInputStream.getUrl( url )
        elif protocol == InputStreamProtocol.TSDECRYPT:
            return TsDecryptInputStream.getUrl( url )
        elif protocol == InputStreamProtocol.MOCK:
            return MockInputStream.getUrl( url )
        return None

defaultConfig.append( InputStreamAbstract )

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
            self._logger.error( "Cannot open multicast: %s:%i" % ( self._ip, self._port ) )
            return False
        return True

    def close( self ):
        self._socket.close()

    def read( self, length ):
        data        = ""
        dataLen     = 0
        prevDataLen = 0
        while ( dataLen < length ):
            data   += self._socket.recv( length )
            dataLen = len( data )
            if dataLen == prevDataLen:
                break
            prevDataLen = dataLen
        return data

    @classmethod
    def getUrl( cls, url ):
        if url.arguments == ";rtpskip=yes":
            protocol = "rtp"
        else:
            protocol = "udp"

        return protocol + "://%s:%d" % ( url.ip, url.port )

class UdpInputStream( InputStreamAbstract ):
    _logger = logging.getLogger( "aminopvr.UdpInputStream" )

    def __init__( self, ip, port ):
        InputStreamAbstract.__init__( self )

        self._ip     = ip
        self._port   = port
        self._socket = None

    def open( self ):
        try:
            self._socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP )
            self._socket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
            if hasattr( socket, "SO_REUSEPORT" ):
                self._socket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEPORT, 1 )
            self._socket.bind( ('', self._port) )
        except:
            self._logger.error( "Cannot open Udp: %s:%i" % ( self._ip, self._port ) )
            return False
        return True

    def close( self ):
        self._socket.close()

    def read( self, length ):
        data        = ""
        dataLen     = 0
        prevDataLen = 0
        while ( dataLen < length ):
            data   += self._socket.recv( length )
            dataLen = len( data )
            if dataLen == prevDataLen:
                break
            prevDataLen = dataLen
        return data

    @classmethod
    def getUrl( cls, url ):
        if url.arguments == ";rtpskip=yes":
            protocol = "rtp"
        else:
            protocol = "udp"

        return protocol + "://%s:%d" % ( url.ip, url.port )

class TsDecryptInputStream( UdpInputStream ):
    _logger = logging.getLogger( "aminopvr.TsDecryptInputStream" )

    _inUse  = []

    def __init__( self, url ):
        useIp = 1
        for number in self._inUse:
            if number >= useIp:
                useIp = number + 1

        self._useIp = useIp
        self._inUse.append( useIp )

        inputStreamConfig = InputStreamConfig( Config() )

        ip      = "127.0.0.1"
        port    = int( inputStreamConfig.tsdecryptBasePort ) + useIp

        self._tsdecrypt = TsDecrypt( url, ip, port )
        UdpInputStream.__init__( self, ip, port )

    def __del__( self ):
        try:
            self.close()
        except:
            pass
        self._tsdecrypt.terminate()
        self._inUse.remove( self._useIp )
        self._logger.info( "TsDecryptInputStream object destroyed" )

    def close( self ):
        super( TsDecryptInputStream, self ).close()
        self._tsdecrypt.terminate()

    @classmethod
    def getUrl( cls, url ):
        return "/channels/%d" % ( url.id )

class HttpInputStream( InputStreamAbstract ):
    _logger = logging.getLogger( "aminopvr.HttpInputStream" )

    def __init__( self, url ):
        InputStreamAbstract.__init__( self )
        self._url      = url
        self._request  = None
        self._response = None

    def open( self ):

        url    = self.getUrl( self._url )
        result = urlparse.urlparse( url )
        self._logger.info( "HttpInputStream.open: url=%s, netloc=%s, path=%s" % ( url, result.netloc, result.path ) )
#        try:
#            self._request = urllib2.urlopen( self._url, timeout=2.5 )
#        except urllib2.HTTPError, e:
#            self._logger.warning( "Cannot open url: %s" % ( self._url ) )
#            self._logger.warning( "HTTP Error code: %d" % e.code )
#            return False
#        except urllib2.URLError, e:
#            self._logger.warning( "Cannot open url: %s" % ( self._url ) )
#            self._logger.warning( "URL Error reason: %s" % e.reason )
#            return False
#        except:
#            self._logger.warning( "Cannot open url: %s" % ( self._url ) )
#            return False
        self._request = httpplus.HTTPConnection( result.netloc, timeout=2.5 )
        try:
            self._request.request( "GET", result.path )
            self._response = self._request.getresponse()
        except httpplus.HTTPTimeoutException, e:
            self._logger.warning( "Cannot open url: %s" % ( url ) )
            self._logger.warning( "HTTPTimeoutException reason: %r" % ( e ) )
            return False
        except httpplus.HTTPStateError, e:
            self._logger.warning( "Cannot open url: %s" % ( url ) )
            self._logger.warning( "HTTPStateError reason: %r" % ( e ) )
            return False
        except httpplus.HTTPRemoteClosedError, e:
            self._logger.warning( "Cannot open url: %s" % ( url ) )
            self._logger.warning( "HTTPRemoteClosedError reason: %r" % ( e ) )
            return False
        except socket.error, e:
            self._logger.warning( "Cannot open url: %s" % ( url ) )
            self._logger.warning( "socket.error reason: %r" % ( e ) )
            return False

        if not self._response:
            return False

        return True

    def close( self ):
        self._request.close()

    def read( self, length ):
        data = None
        try:
            data = self._response.read( length )
        except httpplus.HTTPTimeoutException:
            pass
        return data

    @classmethod
    def getUrl( cls, url ):
        if url.arguments == ";rtpskip=yes":
            protocol = "rtp"
        else:
            protocol = "udp"

        inputStreamConfig = InputStreamConfig( Config() )
        httpBaseUrl       = inputStreamConfig.httpBaseUrl
        formatMap = {
                        "[protocol]": protocol,
                        "[ip]":       url.ip,
                        "[port]":     str( url.port )
                    }

        return reduce( lambda x, y: x.replace( y, formatMap[y] ), formatMap, httpBaseUrl )

class MockInputStream( InputStreamAbstract ):
    _logger = logging.getLogger( "aminopvr.UdpInputStream" )

    def __init__( self, ip, port ):
        InputStreamAbstract.__init__( self )

        self._ip     = ip
        self._port   = port

    def open( self ):
        return True

    def close( self ):
        pass

    def read( self, length ):
        time.sleep( 0.01 )
        return ""

    @classmethod
    def getUrl( cls, url ):
        return "mock://%s:%d" % ( url.ip, url.port )

def main():
    sys.stderr.write( "main()\n" );
    stream = TsDecryptInputStream( "224.5.5.6", 1234 )
    if stream.open():
        sys.stderr.write( "Opened stream\n" )
        while True:
            data = stream.read( 188 * 10 )
            sys.stderr.write( "read %d bytes.\n" % ( len( data ) ) );
    else:
        sys.stderr.write( "Could not open stream\n" )

# allow this to be a module
if __name__ == '__main__':
    import sys
    from aminopvr.channel import ChannelUrl
    main()
