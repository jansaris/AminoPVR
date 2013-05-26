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

from aminopvr.channel import Channel, ChannelUrl, PendingChannel, \
    PendingChannelUrl
import test_lib as test
import unittest


class ChannelTests( test.AminoPVRTestDBCase ):

    def setUp( self ):
        super( ChannelTests, self ).setUp()
        self.db = test.db.DBConnection()

    def tearDown( self ):
        del self.db
        super( ChannelTests, self ).tearDown()

    def test_addChannel( self ):
        channel      = test.createChannel( Channel, 1 )
        channel.urls = { "sd": test.createChannelUrl( ChannelUrl, "sd" ) }
        channel.addToDb( self.db )
        self.assertNotEqual( channel.id, -1, "Channel Id is still -1" )

    def test_getChannel( self ):
        channel      = test.createChannel( Channel, 1 )
        channel.urls = { "sd": test.createChannelUrl( ChannelUrl, "sd" ) }
        channel.addToDb( self.db )

        getChannel = Channel.getByNumberFromDb( self.db, 1 )
        self.assertIsNotNone( getChannel, "Channel does not exist in database" )
        self.assertEqual( channel, getChannel, "Added channel not equal to channel in database" )

    def test_addChannelUrl( self ):
        channel      = test.createChannel( Channel, 1 )
        channel.urls = { "sd": test.createChannelUrl( ChannelUrl, "sd" ) }
        channel.addToDb( self.db )

        channel            = Channel.getFromDb( self.db, channel.id )
        channelUrl         = test.createChannelUrl( ChannelUrl, "hd", True )
        channel.urls["hd"] = channelUrl
        channel.addToDb( self.db )

        channel = Channel.getFromDb( self.db, channel.id )
        self.assertEqual( channel.urls["hd"], channelUrl, "Added channel url not equal to channel url in database" )

    def test_deleteChannel( self ):
        channel      = test.createChannel( Channel, 1 )
        channel.urls = { "sd": test.createChannelUrl( ChannelUrl, "sd" ) }
        channel.addToDb( self.db )

        channel = Channel.getFromDb( self.db, channel.id )
        channel.deleteFromDb( self.db )

        getChannel = Channel.getFromDb( self.db, channel.id )
        self.assertIsNone( getChannel, "Channel still in database" )

        urls = ChannelUrl.getAllFromDb( self.db, channel.id )
        self.assertEqual( urls, {}, "Channel url(s) still in database" )

    def test_deleteChannelUrl( self ):
        channel      = test.createChannel( Channel, 1 )
        channel.urls = { "sd": test.createChannelUrl( ChannelUrl, "sd" ),
                         "hd": test.createChannelUrl( ChannelUrl, "hd", True ) }
        channel.addToDb( self.db )

        channel = Channel.getFromDb( self.db, channel.id )
        del channel.urls["hd"]
        channel.addToDb( self.db )

        channel = Channel.getFromDb( self.db, channel.id )
        self.assertNotIn( "hd", channel.urls, "Hd channel url still in channel" )

    def test_pendingChannelToChannel( self ):
        pendingChannel = test.createChannel( PendingChannel, 1 )
        pendingChannel.urls = { "sd": test.createChannelUrl( PendingChannelUrl, "sd" ) }
        pendingChannel.addToDb( self.db )

        pendingChannel = PendingChannel.getFromDb( self.db, pendingChannel.id )
        channel = Channel.copy( pendingChannel )

        self.assertIsInstance( channel, Channel, "Channel not of type Channel" )
        for channelType in channel.urls.keys():
            self.assertIsInstance( channel.urls[channelType], ChannelUrl, "Channel url not of type ChannelUrl" )

        channel.addToDb( self.db )

        channel = Channel.getFromDb( self.db, channel.id )
        self.assertIsNotNone( channel, "Channel does not exist in database" )
        self.assertEqual( pendingChannel, channel, "Added pending channel not equal to channel in database" )

        pendingChannel.deleteFromDb( self.db )

        getPendingChannel = PendingChannel.getFromDb( self.db, pendingChannel.id )
        self.assertIsNone( getPendingChannel, "Pending channel still in database" )

        urls = PendingChannelUrl.getAllFromDb( self.db, pendingChannel.id )
        self.assertEqual( urls, {}, "Pending channel url(s) still in database" )

    def test_pendingChannelToExistingChannel( self ):
        channel      = test.createChannel( Channel, 1 )
        channel.urls = { "sd": test.createChannelUrl( PendingChannelUrl, "sd" ) }
        channel.addToDb( self.db )

        pendingChannel = test.createChannel( PendingChannel, 2 )
        pendingChannel.urls = { "sd": test.createChannelUrl( ChannelUrl, "sd" ),
                                "hd": test.createChannelUrl( ChannelUrl, "sd", True ) }
        pendingChannel.addToDb( self.db )

        pendingChannel = PendingChannel.getFromDb( self.db, pendingChannel.id )
        updatedChannel = Channel.copy( pendingChannel, channel.id )

        self.assertIsInstance( updatedChannel, Channel, "Channel not of type Channel" )
        for channelType in updatedChannel.urls.keys():
            self.assertIsInstance( updatedChannel.urls[channelType], ChannelUrl, "Channel url not of type ChannelUrl" )

        updatedChannel.addToDb( self.db )
        self.assertEqual( updatedChannel.id, channel.id, "Channel Id not equal to original channel Id" )

        channel = Channel.getFromDb( self.db, channel.id )
        self.assertIsNotNone( channel, "Channel does not exist in database" )
        self.assertEqual( pendingChannel, channel, "Added pending channel not equal to channel in database" )

    def test_getActiveAndInactiveChannels( self ):
        activeChannels   = [ test.createChannel( Channel, x )                     for x in range( 5 ) ]
        inactiveChannels = [ test.createChannel( Channel, x + 10, inactive=True ) for x in range( 5 ) ]

        for channel in activeChannels:
            channel.addToDb( self.db )
        for channel in inactiveChannels:
            channel.addToDb( self.db )

        getActiveChannels = Channel.getAllFromDb( self.db, includeInactive=False )
        self.assertSetEqual( set( activeChannels ), set( getActiveChannels ), "Active channels added not equal to active channels in database" )

        getAllChannels = Channel.getAllFromDb( self.db, includeInactive=True )
        self.assertSetEqual( set( activeChannels ) | set( inactiveChannels ), set( getAllChannels ), "All channels added not equal to all channels in database" )

    def test_getRadioAndTvChannels( self ):
        tvChannels    = [ test.createChannel( Channel, x )                  for x in range( 5 ) ]
        radioChannels = [ test.createChannel( Channel, x + 10, radio=True ) for x in range( 5 ) ]

        for channel in tvChannels:
            channel.addToDb( self.db )
        for channel in radioChannels:
            channel.addToDb( self.db )

        getTvChannels = Channel.getAllFromDb( self.db )
        self.assertSetEqual( set( tvChannels ), set( getTvChannels ), "Tv channels added not equal to tv channels in database" )

        getRadioChannels = Channel.getAllFromDb( self.db, includeRadio=True, tv=False )
        self.assertSetEqual( set( radioChannels ), set( getRadioChannels ), "Radio channels add not equal to radio channels in database" )

        getAllChannels = Channel.getAllFromDb( self.db, includeRadio=True, tv=True )
        self.assertSetEqual( set( tvChannels ) | set( radioChannels ), set( getAllChannels ), "All channels add not equal to all channels in database" )

if __name__ == '__main__':
    print "=================="
    print "STARTING - Channel TESTS"
    print "=================="
    print "######################################################################"
    suite = unittest.TestLoader().loadTestsFromTestCase( ChannelTests )
    unittest.TextTestRunner( verbosity=2 ).run( suite )
