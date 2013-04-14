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
from aminopvr.db import DBConnection
from aminopvr.input_stream import InputStreamAbstract, InputStreamProtocol
from aminopvr.tools import getPage
import copy
import logging
import os
import sys
import urlparse

class ChannelUrlAbstract( object ):

    _tableName   = None

    def __init__( self, channelType, protocol, ip, port, arguments, scrambled=0 ):
        self._channelType = unicode( channelType )
        self._protocol    = unicode( protocol )
        self._ip          = unicode( ip )
        self._port        = int( port )
        self._arguments   = unicode( arguments )
        self._scrambled   = int( scrambled )

        self._logger.debug( 'ChannelUrl.__init__( channelType=%s, protocol=%s, ip=%s, port=%i, arguments=%s )' % ( channelType, protocol, ip, port, arguments ) )

    def __hash__( self ):
        return ( hash( hash( self._channelType ) +
                       hash( self._protocol ) +
                       hash( self._ip ) +
                       hash( self._port ) +
                       hash( self._arguments ) +
                       hash( self._scrambled ) ) )

    def __eq__( self, other ):
        return ( self._channelType == other._channelType and
                 self._protocol    == other._protocol    and
                 self._ip          == other._ip          and
                 self._port        == other._port        and
                 self._arguments   == other._arguments   and
                 self._scrambled   == other._scrambled )

    def __ne__( self, other ):
        return not self.__eq__( other )

    def __str__( self ):
        return ( "%s://%s:%i%s" % ( self._protocol, self._ip, self._port, self.arguments ) )

    @classmethod
    def copy( cls, channelUrl ):
        if isinstance( channelUrl, ChannelUrlAbstract ):
            channelUrl = copy.copy( channelUrl )
            channelUrl.__class__ = cls
            return channelUrl
        return None

    @property
    def channelType( self ):
        return self._channelType

    @property
    def protocol( self ):
        return self._protocol

    @protocol.setter
    def protocol( self, protocol ):
        self._protocol = unicode( protocol )

    @property
    def ip( self ):
        return self._ip

    @ip.setter
    def ip( self, ip ):
        self._ip = unicode( ip )

    @property
    def port( self ):
        return self._port

    @port.setter
    def port( self, port ):
        self._port = int( port )

    @property
    def arguments( self ):
        return self._arguments

    @arguments.setter
    def arguments( self, arguments ):
        self._arguments = unicode( arguments )

    @property
    def scrambled( self ):
        return self._scrambled

    @scrambled.setter
    def scrambled( self, scrambled ):
        self._scrambled = int( scrambled )

    @classmethod
    def getAllFromDb( cls, conn, channelId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        urls = {}
        if conn:
            rows = conn.execute( "SELECT * FROM %s WHERE channel_id=?" % ( cls._tableName ), ( channelId, ) )
            for row in rows:
                urls[unicode( row["type"] )] = cls._createChannelUrlFromDbDict( row )

        return urls

    @classmethod
    def getFromDb( cls, conn, channelId, channelType ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        url = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE channel_id=? AND type=?" % ( cls._tableName ), ( channelId, channelType ) )
            if row:
                url = cls._createChannelUrlFromDbDict( row[0] )

        return url

    @classmethod
    def getChannelByIpPortFromDb( cls, conn, ip, port ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        if conn:
            row = conn.execute( "SELECT channel_id FROM %s WHERE ip=? AND port=?" % ( cls._tableName ), ( ip, port ) )
            if row:
                return row[0]["channel_id"]
        return None

    @classmethod
    def _createChannelUrlFromDbDict( cls, channelUrlData ):
        url = None
        if channelUrlData:
            url = cls( channelUrlData["type"], channelUrlData["protocol"], channelUrlData["ip"], channelUrlData["port"], channelUrlData["arguments"], channelUrlData["scrambled"] )
        return url

    def addToDb( self, conn, channelId ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
            channelUrl = self.getFromDb( conn, channelId, self._channelType )
            if channelUrl:
                if self != channelUrl:
                    conn.execute( "UPDATE %s SET protocol=?, ip=?, port=?, arguments=?, scrambled=? WHERE channel_id=? AND type=?" % ( self._tableName ), ( self._protocol, self._ip, self._port, self._arguments, self._scrambled, channelId, self._channelType ) )
            else:
                conn.insert( "INSERT INTO %s (channel_id, type, protocol, ip, port, arguments, scrambled) VALUES (?, ?, ?, ?, ?, ?, ?)" % ( self._tableName ), ( channelId, self._channelType, self._protocol, self._ip, self._port, self._arguments, self._scrambled ) )

    @classmethod
    def deleteByChannelIdFromDb( cls, conn, channelId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        if conn:
            conn.execute( "DELETE FROM %s WHERE channel_id=?" % ( cls._tableName ), ( channelId, ) )

    def deleteFromDb( self, conn, channelId ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
            conn.execute( "DELETE FROM %s WHERE channel_id=? AND type=?" % ( self._tableName ), ( channelId, self._channelType ) )

    def getUrl( self, protocol ):
        return InputStreamAbstract.getUrl( protocol, self )

    def dump( self ):
        return ( "{%r, %s://%s:%i%s}" % ( self._channelType, self._protocol, self._ip, self._port, self._arguments ) )

class ChannelUrl( ChannelUrlAbstract ):
    _tableName = "channel_urls"
    _logger    = logging.getLogger( 'aminopvr.Channel.Url' )

class PendingChannelUrl( ChannelUrlAbstract ):
    _tableName = "pending_channel_urls"
    _logger    = logging.getLogger( 'aminopvr.PendingChannel.Url' )

class ChannelAbstract( object ):

    _tableName       = None
    _channelUrlClass = None

    def __init__( self, id, number, epgId, name, nameShort, logo, thumbnail, radio, inactive ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        assert self._channelUrlClass != None, "Not the right class: %r" % ( self )

        self._id         = int( id )
        self._number     = int( number )
        self._epgId      = unicode( epgId )
        self._name       = unicode( name )
        self._nameShort  = unicode( nameShort )
        self._logo       = unicode( logo )
        self._thumbnail  = unicode( thumbnail )
        self._radio      = int( radio )
        self._inactive   = int( inactive )
        self._urls       = {} 

        self._logger.debug( 'ChannelAbstract.__init__( id=%i, number=%s, epgId=%s, name=%s, nameShort=%s, logo=%s, thumbnail=%s, radio=%i, inactive=%i )' % ( id, number, epgId, name, nameShort, logo, thumbnail, radio, inactive ) )

    def __hash__( self ):
        return ( hash( hash( self._number ) +
                       hash( self._epgId ) +
                       hash( self._name ) +
                       hash( self._nameShort ) +
                       hash( os.path.basename( self._logo ) ) +
                       hash( os.path.basename( self._thumbnail ) ) +
                       hash( self._radio ) +
                       hash( frozenset( self._urls ) ) +
                       hash( self._inactive ) ) )

    def __eq__( self, other ):
        # Not comparng _id as it might not be set at comparison time.
        # For insert/update descision it is not relevant
        return ( self._epgId                                          == other._epgId                         and
                 self._number                                         == other._number                        and
                 self._name                                           == other._name                          and
                 self._nameShort                                      == other._nameShort                     and
                 os.path.basename( self._logo )                       == os.path.basename( other._logo )      and
                 os.path.basename( self._thumbnail )                  == os.path.basename( other._thumbnail ) and
                 self._radio                                          == other._radio                         and
                 set( self._urls ).intersection( set( other._urls ) ) == set( self._urls )                    and
                 self._inactive                                       == other._inactive )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @classmethod
    def copy( cls, channel, id=-1 ):
        if isinstance( channel, ChannelAbstract ):
            channel = copy.copy( channel )
            channel.__class__ = cls
            channel._id       = id

            urls    = []
            for key in channel._urls.keys():
                urls.append( cls._channelUrlClass.copy( channel._urls[key] ) )
            channel._urls = {}
            for url in urls:
                channel.addUrl( url )
            return channel
        return None

    def addUrl( self, url ):
        urlType = unicode( url.channelType )
        if self._urls.has_key( urlType ):
            if self._urls[urlType] != url:
                self._urls[urlType].protocol  = url.protocol
                self._urls[urlType].ip        = url.ip
                self._urls[urlType].port      = url.port
                self._urls[urlType].arguments = url.arguments
        else:
            self._urls[urlType] = url

    @property
    def id( self ):
        return self._id

    @property
    def number( self ):
        return self._number

    @number.setter
    def number( self, number ):
        self._number = int( number )

    @property
    def epgId( self ):
        return self._epgId

    @epgId.setter
    def epgId( self, epgId ):
        self._epgId = unicode( epgId )

    @property
    def name( self ):
        return self._name

    @name.setter
    def name( self, name ):
        self._name = unicode( name )

    @property
    def nameShort( self ):
        return self._nameShort

    @nameShort.setter
    def nameShort( self, nameShort ):
        self._nameShort = unicode( nameShort )

    @property
    def logo( self ):
        return self._logo

    @logo.setter
    def logo( self, logo ):
        self._logo = unicode( logo )

    @property
    def thumbnail( self ):
        return self._thumbnail

    @thumbnail.setter
    def thumbnail( self, thumbnail ):
        self._thumbnail = unicode( thumbnail )

    @property
    def radio( self ):
        return self._radio

    @radio.setter
    def radio( self, radio ):
        self._radio = int( radio )

    @property
    def inactive( self ):
        return self._inactive

    @inactive.setter
    def inactive( self, inactive ):
        self._inactive = int( inactive )

    @property
    def urls( self ):
        return self._urls

    @urls.setter
    def urls( self, urls ):
        self._urls = urls

    @classmethod
    def getAllByEpgIdFromDb( cls, conn, epgId, includeInactive=False, includeRadio=False ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        channels = []
        if conn:
            rows = None
            whereCondition = [ "epg_id=?" ]
            if not includeInactive:
                whereCondition.append( "inactive=0" )
            if not includeRadio:
                whereCondition.append( "radio=0" )
            rows = conn.execute( "SELECT * FROM %s WHERE %s ORDER BY number ASC" % ( cls._tableName, " AND ".join( whereCondition ) ), ( epgId, ) )
            for row in rows:
                channel = cls._createChannelFromDbDict( conn, row )
                channels.append( channel )

        return channels

    @classmethod
    def getAllFromDb( cls, conn, includeInactive=False, includeRadio=False, tv=True ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        channels = []
        if conn:
            rows = None
            whereCondition = []
            if not includeInactive:
                whereCondition.append( "inactive=0" )
            if not includeRadio:
                whereCondition.append( "radio=0" )
            if not tv and includeRadio:
                whereCondition.append( "radio=1" )
            if len( whereCondition ) > 0:
                rows = conn.execute( "SELECT * FROM %s WHERE %s ORDER BY number ASC" % ( cls._tableName, " AND ".join( whereCondition ) ) )
            else:
                rows = conn.execute( "SELECT * FROM %s ORDER BY number ASC" % ( cls._tableName ) )
            for row in rows:
                channel = cls._createChannelFromDbDict( conn, row )
                channels.append( channel )

        return channels

    @classmethod
    def getUniqueEpgIdsFromDb( cls, conn, includeInactive=False, includeRadio=False ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        epgIds = []
        if conn:
            rows = None
            whereCondition = []
            if not includeInactive:
                whereCondition.append( "inactive=0" )
            if not includeRadio:
                whereCondition.append( "radio=0" )
            if len( whereCondition ) > 0:
                rows = conn.execute( "SELECT DISTINCT epg_id FROM %s WHERE %s ORDER BY number ASC" % ( cls._tableName, " AND ".join( whereCondition ) ) )
            else:
                rows = conn.execute( "SELECT DISTINCT epg_id FROM %s ORDER BY number ASC" % ( cls._tableName ) )
            for row in rows:
                epgIds.append( row["epg_id"] )

        return epgIds

    @classmethod
    def getFromDb( cls, conn, id ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        channel = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE id=?" % ( cls._tableName ), ( id, ) )
            if row:
                channel = cls._createChannelFromDbDict( conn, row[0] )
        return channel

    @classmethod
    def getByNumberFromDb( cls, conn, number ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        channel = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE number=?" % ( cls._tableName ), ( number, ) )
            if row:
                channel = cls._createChannelFromDbDict( conn, row[0] )
        return channel

    @classmethod
    def getNumChannelsFromDb( cls, conn, includeInactive=False, includeRadio=False ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        numChannels = 0
        if conn:
            rows = None
            whereCondition = []
            if not includeInactive:
                whereCondition.append( "inactive=0" )
            if not includeRadio:
                whereCondition.append( "radio=0" )
            if len( whereCondition ) > 0:
                row = conn.execute( "SELECT COUNT(*) AS num_channels FROM %s WHERE %s" % ( cls._tableName, " AND ".join( whereCondition ) ) )
            else:
                row = conn.execute( "SELECT COUNT(*) AS num_channels FROM %s" % ( cls._tableName ) )
            numChannels = row[0]["num_channels"]
        return numChannels

    @classmethod
    def _createChannelFromDbDict( cls, conn, channelData ):
        channel = None
        if channelData:
            channel = cls( channelData["id"],
                           channelData["number"],
                           channelData["epg_id"],
                           channelData["name"],
                           channelData["name_short"],
                           channelData["logo"],
                           channelData["thumbnail"],
                           channelData["radio"],
                           channelData["inactive"] )
            channel.getUrlsFromDb( conn )
        return channel

    def getUrlsFromDb( self, conn ):
        self._urls = self._channelUrlClass.getAllFromDb( conn, self._id )

    def addToDb( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
            channel = None
            if self._id != -1:
                channel = self.getFromDb( conn, self._id )
                if not channel:
                    self._id = -1

            if self._id != -1:
                if channel and self != channel:
                    conn.execute( "UPDATE %s SET number=?, epg_id=?, name=?, name_short=?, logo=?, thumbnail=?, radio=?, inactive=? WHERE id=?" % ( self._tableName ), ( self._number, self._epgId, self._name, self._nameShort, self._logo, self._thumbnail, self._radio, self._inactive, self._id ) )
            else:
                id = conn.insert( "INSERT INTO %s (number, epg_id, name, name_short, logo, thumbnail, radio, inactive) VALUES (?, ?, ?, ?, ?, ?, ?, ?)" % ( self._tableName ), ( self._number, self._epgId, self._name, self._nameShort, self._logo, self._thumbnail, self._inactive, self._radio ) )
                if id:
                    self._id = id;

            if self._id:
                urls = self._channelUrlClass.getAllFromDb( conn, self._id )
                for key in urls.keys():
                    if not self._urls.has_key( key ):
                        urls[key].deleteFromDb( conn, self._id )
                for key in self._urls.keys():
                    self._urls[key].addToDb( conn, self._id )

    def deleteFromDb( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
            conn.execute( "DELETE FROM %s WHERE id=?" % ( self._tableName ), ( self._id, ) )
            self._channelUrlClass.deleteByChannelIdFromDb( conn, self._id )

#    def getM3UEntry( self, unicast ):
#        output = ""
#        has_hd = False
#
#        for url in self.urls:
#            if url.channel_type == "hd":
#                has_hd = True
#                break
#
#        for url in self.urls:
#            channel_name   = self.name
#            channel_number = self.number
#            if url.channel_type == "sd" and has_hd:
#                channel_name   = channel_name + " SD"
#                channel_number = channel_number + 9000
#
#            output = output + "#EXTINF:-1,%i - %s\n" % ( channel_number, filter_line( channel_name ) )
#            output = output + "#EXTMYTHTV:xmltvid=%s\n" % ( self.epg_id )
#            output = output + "%s\n" % ( url.getUrl( unicast ) )
#
#        return output

    def getChannelUrl( self, protocol=InputStreamProtocol.HTTP, includeScrambled=False, includeHd=True ):
        channelUrl = None

        if includeHd and self._urls.has_key( "hd" ):
            if self._urls["hd"].scrambled and includeScrambled:
                channelUrl = self._urls["hd"]
            elif not self._urls["hd"].scrambled:
                channelUrl = self._urls["hd"]
        if not channelUrl:
            if self._urls.has_key( "sd" ):
                if self._urls["sd"].scrambled and includeScrambled:
                    channelUrl = self._urls["sd"]
                elif not self._urls["sd"].scrambled:
                    channelUrl = self._urls["sd"]
        if channelUrl:
            return channelUrl.getUrl( protocol )
        else:
            return None

    def toDict( self, protocol=InputStreamProtocol.HTTP, includeScrambled=False, includeHd=True ):
        channelUrl = self.getChannelUrl( protocol, includeScrambled, includeHd )
        if channelUrl:
            return { "id": self.id, "number": self.number, "name": self.name, "url": channelUrl, "logo_path": "/assets/images/channels/logos/" + self.logo }
        else:
            return None

    def dump( self ):
        radio = self._radio and ", radio" or ""
        urls  = ""
        for key in self._urls.keys():
            if urls != "":
                urls = urls + ", "
            urls = urls + self._urls[key].dump()
        return ( "%i: %i - %r (%r, %r, %r, %r, [%s]%s)" % ( self._id, self._number, self._name, self._epgId, self._nameShort, self._logo, self._thumbnail, urls, radio ) )

class Channel( ChannelAbstract ):
    _tableName       = "channels"
    _channelUrlClass = ChannelUrl
    _logger          = logging.getLogger( 'aminopvr.Channel' )

    def downloadLogoAndThumbnail( self ):
        if self._logo != "" and self._logo.startswith( "http://" ):
            logoFilename   = urlparse.urlsplit( self._logo )[2].split( '/' )[-1]
            logoPath       = os.path.join( DATA_ROOT, "assets/images/channels/logos", logoFilename )
            filename, _, _ = getPage( self._logo, logoPath )
            if filename:
                self._logo = logoFilename
                self._logger.info( "Channel.downloadLogoAndThumbnail: downloaded logo to %s" % ( logoPath ) )
            else:
                self._logger.info( "Channel.downloadLogoAndThumbnail: could not download logo from %s" % ( self._logo ) )
                self._logo = ""
        if self._thumbnail != "" and self._thumbnail.startswith( "http://" ):
            thumbnailFilename = urlparse.urlsplit( self._thumbnail )[2].split( '/' )[-1]
            thumbnailPath     = os.path.join( DATA_ROOT, "assets/images/channels/thumbnails", thumbnailFilename )
            filename, _, _    = getPage( self._thumbnail, thumbnailPath )
            if filename:
                self._thumbnail = thumbnailFilename
                self._logger.info( "Channel.downloadLogoAndThumbnail: downloaded thumbnail to %s" % ( thumbnailPath ) )
            else:
                self._logger.info( "Channel.downloadLogoAndThumbnail: could not download thumbnail from %s" % ( self._thumbnail ) )
                self._thumbnail = ""

#    def removeLogo( self ):
#        # TODO check if logo is used by other channel
#        # if not, unlink the file
#
#    def removeThumbnail( self ):
#        # TODO check if logo is used by other channel
#        # if not, unlink the file

class PendingChannel( ChannelAbstract ):
    _tableName       = "pending_channels"
    _channelUrlClass = PendingChannelUrl
    _logger          = logging.getLogger( 'aminopvr.PendingChannel' )

def main():
    conn = DBConnection( "aminopvr.db" )

    if conn:
        rows = conn.execute( "SELECT * FROM channels WHERE name LIKE ?", ["%een%"] )
        for row in rows:
            sys.stderr.write( "%s\n" % ( row["name"]) )

    channel = Channel.getFromDb( conn, 1489 )
#    channel.addUrl( ChannelUrl( "hd", "igmp", "123.321.123.321", 1241, "" ) )
#    channel.addUrl( ChannelUrl( "sd", "igmp", "321.123.321.123", 1421, "skiprtp=yes" ) )
    otherChannel = PendingChannel( -1, 1, "ned1", "Nederland 1", "Nederland 1", "ned1.png", "ned1.png", False, False )
    otherChannel.addUrl( PendingChannelUrl( "sd", "igmp", "233.81.233.161", 10294, "", False ) )
    otherChannel.addUrl( PendingChannelUrl( "hd", "igmp", "224.1.3.1", 12110, "", False ) )
    if channel == otherChannel:
        sys.stderr.write( "Channels are equal\n" )
    else:
        sys.stderr.write( "Channels are not equal\n" )

#    channel = Channel.getFromDb( conn, 1 )
#    if not channel:
#        channel = Channel( -1, 1, "ned1", "Nederland 2", "Ned 1", "logo.png", "thumbnail.png", 0 )
#        channel.addUrl( ChannelUrl( "hd", "igmp", "123.321.123.321", 1241, "" ) )
#        channel.addUrl( ChannelUrl( "sd", "igmp", "321.123.321.123", 1421, "skiprtp=yes" ) )
#        channel.addToDb( conn )
#    sys.stderr.write( channel.dump() )

# allow this to be a module
if __name__ == '__main__':
    main()
