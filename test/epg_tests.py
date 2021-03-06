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

from aminopvr.channel import Channel
from aminopvr.epg import EpgId, EpgProgram, EpgProgramGenre, Genre, Person, \
    EpgProgramActor, EpgProgramDirector, EpgProgramPresenter
from aminopvr.tools import getTimestamp
import test_lib as test # import test_lib before anything else from aminopvr!
import unittest


class EpgIdTests( test.AminoPVRTestDBCase ):

    def setUp( self ):
        super( EpgIdTests, self ).setUp()
        self.db = test.db.DBConnection()

    def tearDown( self ):
        del self.db
        super( EpgIdTests, self ).tearDown()

    def test_addAndGetEpgId( self ):
        epgId = self._createEpgId( 1 )
        epgId.addToDb( self.db )

        getEpgId = EpgId.getFromDb( self.db, epgId.epgId )
        self.assertIsNotNone( getEpgId, "EpgId does not exist in database" )
        self.assertEqual( epgId, getEpgId, "Added EpgId not equal to epgId in database" )

    def test_deleteEpgId( self ):
        epgId = self._createEpgId( 1 )
        epgId.addToDb( self.db )

        epgId.getFromDb( self.db, epgId.epgId )
        epgId.deleteFromDb( self.db )

        getEpgId = EpgId.getFromDb( self.db, epgId.epgId )
        self.assertIsNone( getEpgId, "EpgId still in database" )

    def test_getEpgIds( self ):
        activeChannels   = [ test.createChannel( Channel, x )                     for x in range( 5 ) ]
        inactiveChannels = [ test.createChannel( Channel, x + 10, inactive=True ) for x in range( 5 ) ]
        activeEpgIds     = [ EpgId( channel.epgId, "full" )                       for channel in activeChannels ]
        inactiveEpgIds   = [ EpgId( channel.epgId, "full" )                       for channel in inactiveChannels ]

        for channel in activeChannels:
            channel.addToDb( self.db )
        for channel in inactiveChannels:
            channel.addToDb( self.db )
        for epgId in activeEpgIds:
            epgId.addToDb( self.db )
        for epgId in inactiveEpgIds:
            epgId.addToDb( self.db )

        epgIds = EpgId.getAllFromDb( self.db )
        self.assertSetEqual( set( activeEpgIds ), set( epgIds ), "Active channels/epgIds added not equal to active epgIds/channels in database" )

    def test_getTvAndRadioEpgIds( self ):
        tvChannels    = [ test.createChannel( Channel, x )                  for x in range( 5 ) ]
        radioChannels = [ test.createChannel( Channel, x + 10, radio=True ) for x in range( 5 ) ]
        tvEpgIds      = [ EpgId( channel.epgId, "full" )                    for channel in tvChannels ]
        radioEpgIds   = [ EpgId( channel.epgId, "full" )                    for channel in radioChannels ]

        for channel in tvChannels:
            channel.addToDb( self.db )
        for channel in radioChannels:
            channel.addToDb( self.db )
        for epgId in tvEpgIds:
            epgId.addToDb( self.db )
        for epgId in radioEpgIds:
            epgId.addToDb( self.db )

        epgIds = EpgId.getAllFromDb( self.db )
        self.assertSetEqual( set( tvEpgIds ), set( epgIds ), "Tv channels/epgIds added not equal to tv epgIds/channels in database" )

        epgIds = EpgId.getAllFromDb( self.db, includeRadio=True )
        self.assertSetEqual( set( tvEpgIds ) | set( radioEpgIds ), set( epgIds ), "All channels/epgIds added not equal to all epgIds/channels in database" )

    def _createEpgId( self, number, strategy="full" ):
        return EpgId( "test_%i" % ( number ), strategy )

class EpgProgramTests( test.AminoPVRTestDBCase ):

    def setUp( self ):
        super( EpgProgramTests, self ).setUp()
        self.db = test.db.DBConnection()

    def tearDown( self ):
        del self.db
        super( EpgProgramTests, self ).tearDown()

    def test_addProgram( self ):
        program            = self._createProgram( EpgProgram, 1 )
        program.genres     = [ self._createProgramGenre(  EpgProgramGenre,     1 ) ]
        program.actors     = [ self._createProgramPerson( EpgProgramActor,     1 ) ]
        program.directors  = [ self._createProgramPerson( EpgProgramDirector,  1 ) ]
        program.presenters = [ self._createProgramPerson( EpgProgramPresenter, 1 ) ]
        program.addToDb( self.db )
        self.assertNotEqual( program.id, -1, "Program Id is still -1" )

    def test_getChannel( self ):
        program            = self._createProgram( EpgProgram, 1 )
        program.genres     = [ self._createProgramGenre(  EpgProgramGenre,     1 ) ]
        program.actors     = [ self._createProgramPerson( EpgProgramActor,     1 ) ]
        program.directors  = [ self._createProgramPerson( EpgProgramDirector,  1 ) ]
        program.presenters = [ self._createProgramPerson( EpgProgramPresenter, 1 ) ]
        program.addToDb( self.db )

        getProgram = EpgProgram.getFromDb( self.db , program.id )
        self.assertIsNotNone( getProgram, "Program does not exist in database" )
        self.assertEqual( program, getProgram, "Added program not equal to program in database" )

    def test_addGenre( self ):
        program = self._createProgram( EpgProgram, 1 )
        program.addToDb( self.db )

        program.genres.append( self._createProgramGenre( EpgProgramGenre, 1 ) )
        program.addToDb( self.db )

        getProgram = EpgProgram.getFromDb( self.db, program.id )
        self.assertSetEqual( set( getProgram.genres ), set( program.genres ), "Added program genre not equal to program genre in database" )

    def test_addPerson( self ):
        program = self._createProgram( EpgProgram, 1 )
        program.addToDb( self.db )

        programPerson = self._createProgramPerson( EpgProgramActor, 1 )
        program.actors.append( programPerson )
        program.addToDb( self.db )

        getProgram = EpgProgram.getFromDb( self.db, program.id )
        self.assertSetEqual( set( getProgram.actors ), set( program.actors ), "Added program person not equal to program person in database" )

    def test_deleteChannel( self ):
        program            = self._createProgram( EpgProgram, 1 )
        program.genres     = [ self._createProgramGenre(  EpgProgramGenre,     1 ) ]
        program.actors     = [ self._createProgramPerson( EpgProgramActor,     1 ) ]
        program.directors  = [ self._createProgramPerson( EpgProgramDirector,  1 ) ]
        program.presenters = [ self._createProgramPerson( EpgProgramPresenter, 1 ) ]
        program.addToDb( self.db )

        program = EpgProgram.getFromDb( self.db , program.id )
        program.deleteFromDb( self.db )

        getProgram = EpgProgram.getFromDb( self.db, program.id )
        self.assertIsNone( getProgram, "Program still in database" )

        genres = EpgProgramGenre.getAllFromDb( self.db, program.id )
        self.assertEqual( genres, [], "Program genres still in database" )

        actors = EpgProgramActor.getAllFromDb( self.db, program.id )
        self.assertEqual( actors, [], "Program actors still in database" )

        directors = EpgProgramDirector.getAllFromDb( self.db, program.id )
        self.assertEqual( directors, [], "Program directors still in database" )

        presenters = EpgProgramPresenter.getAllFromDb( self.db, program.id )
        self.assertEqual( presenters, [], "Program presenters still in database" )

    def test_deleteGenre( self ):
        genres         = [ self._createProgramGenre(  EpgProgramGenre, x ) for x in range( 2 ) ]
        program        = self._createProgram( EpgProgram, 1 )
        program.genres = [ genre for genre in genres ] 
        program.addToDb( self.db )

        program = EpgProgram.getFromDb( self.db, program.id )
        program.genres.remove( genres[0] )
        program.addToDb( self.db )

        program = EpgProgram.getFromDb( self.db, program.id )
        self.assertNotIn( genres[0], program.genres, "Program genre still in program" )

    def test_deletePerson( self ):
        actors         = [ self._createProgramPerson(  EpgProgramActor, x ) for x in range( 2 ) ]
        program        = self._createProgram( EpgProgram, 1 )
        program.actors = [ actor for actor in actors ] 
        program.addToDb( self.db )

        program = EpgProgram.getFromDb( self.db, program.id )
        program.actors.remove( actors[0] )
        program.addToDb( self.db )

        program = EpgProgram.getFromDb( self.db, program.id )
        self.assertNotIn( actors[0], program.actors, "Program person still in program" )

    def testNowNextPrograms( self ):
        now       = getTimestamp()
        program11 = self._createProgram( EpgProgram, 1, epgId="test_1", startTime=now-600, endTime=now-300 ) # before now
        program12 = self._createProgram( EpgProgram, 2, epgId="test_1", startTime=now-300, endTime=now+300 ) # now
        program13 = self._createProgram( EpgProgram, 3, epgId="test_1", startTime=now+300, endTime=now+600 ) # next
        program14 = self._createProgram( EpgProgram, 4, epgId="test_1", startTime=now+600, endTime=now+900 ) # after next
        program21 = self._createProgram( EpgProgram, 5, epgId="test_2", startTime=now-600, endTime=now-300 ) # before now
        program22 = self._createProgram( EpgProgram, 6, epgId="test_2", startTime=now-300, endTime=now+300 ) # now
        program23 = self._createProgram( EpgProgram, 7, epgId="test_2", startTime=now+300, endTime=now+600 ) # next
        program24 = self._createProgram( EpgProgram, 8, epgId="test_2", startTime=now+600, endTime=now+900 ) # after next
        program11.addToDb( self.db )
        program12.addToDb( self.db )
        program13.addToDb( self.db )
        program14.addToDb( self.db )
        program21.addToDb( self.db )
        program22.addToDb( self.db )
        program23.addToDb( self.db )
        program24.addToDb( self.db )

        nowNextPrograms      = EpgProgram.getNowNextFromDb( self.db )
        nowNextProgramsSet   = set( [ program12, program13, program22, program23 ] )
        nowNextProgramsDbSet = set( nowNextPrograms )
        self.assertSetEqual( nowNextProgramsSet, nowNextProgramsDbSet, "Now/next incorrect" )

    def _createProgram( self, cls, number, epgId="test", subNumber=0, descNumber=0, startTime=0, endTime=300 ):
        program             = cls()
        program.epgId       = epgId
        program.originalId  = "orgid_%i_%i_%i" % ( number, subNumber, descNumber )
        program.startTime   = startTime
        program.endTime     = endTime
        program.title       = "Program %i" % ( number )
        program.subtitle    = "Sub %i" % ( subNumber )
        program.description = "Desc %i" % ( descNumber )
        program.detailed    = True
        return program

    def _createProgramGenre( self, cls, number ):
        genre               = Genre()
        genre.genre         = "Genre %i" % ( number )

        programGenre        = cls()
        programGenre.genre  = genre

        return programGenre

    def _createProgramPerson( self, cls, number ):
        person                  = Person()
        person.person           = "Person<%s> %i" % ( cls.__name__, number )

        programPerson           = cls()
        programPerson.person    = person

        return programPerson

#     def test_getActiveAndInactiveChannels( self ):
#         activeChannels   = [ self._createChannel( Channel, x )                     for x in range( 5 ) ]
#         inactiveChannels = [ self._createChannel( Channel, x + 10, inactive=True ) for x in range( 5 ) ]
# 
#         for channel in activeChannels:
#             channel.addToDb( self.db )
#         for channel in inactiveChannels:
#             channel.addToDb( self.db )
# 
#         getActiveChannels = Channel.getAllFromDb( self.db, includeInactive=False )
#         self.assertSetEqual( set( activeChannels ), set( getActiveChannels ), "Active channels added not equal to active channels in database" )
# 
#         getAllChannels = Channel.getAllFromDb( self.db, includeInactive=True )
#         self.assertSetEqual( set( activeChannels ) | set( inactiveChannels ), set( getAllChannels ), "All channels added not equal to all channels in database" )
# 
#     def test_getRadioAndTvChannels( self ):
#         tvChannels    = [ self._createChannel( Channel, x )                  for x in range( 5 ) ]
#         radioChannels = [ self._createChannel( Channel, x + 10, radio=True ) for x in range( 5 ) ]
# 
#         for channel in tvChannels:
#             channel.addToDb( self.db )
#         for channel in radioChannels:
#             channel.addToDb( self.db )
# 
#         getTvChannels = Channel.getAllFromDb( self.db )
#         self.assertSetEqual( set( tvChannels ), set( getTvChannels ), "Tv channels added not equal to tv channels in database" )
# 
#         getRadioChannels = Channel.getAllFromDb( self.db, includeRadio=True, tv=False )
#         self.assertSetEqual( set( radioChannels ), set( getRadioChannels ), "Radio channels add not equal to radio channels in database" )
# 
#         getAllChannels = Channel.getAllFromDb( self.db, includeRadio=True, tv=True )
#         self.assertSetEqual( set( tvChannels ) | set( radioChannels ), set( getAllChannels ), "All channels add not equal to all channels in database" )
# 
#     def _createChannel( self, cls, number, radio=False, inactive=False ):
#         channel = cls( -1,
#                        number,
#                        "test_%i" % ( number ),
#                        "Test Channel %i" % ( number ),
#                        "Test Chan %i" % ( number ),
#                        "logo.png",
#                        "thumbnail.png",
#                        radio,
#                        inactive
#                       )
#         return channel
# 
#     def _createChannelUrl( self, cls, type, scrambled=False ):
#         ip   = "123.456.987.123"
#         port = 1234
#         if type == "hd":
#             ip   = "321.789.654.321"
#             port = 4321
#         channelUrl = cls( type, "udp", ip, port, "args", scrambled )
#         return channelUrl

if __name__ == '__main__':
    print "=================="
    print "STARTING - EPG TESTS"
    print "=================="
    print "######################################################################"
    suite = unittest.TestLoader().loadTestsFromTestCase( EpgIdTests )
    unittest.TextTestRunner( verbosity=2 ).run( suite )
    suite = unittest.TestLoader().loadTestsFromTestCase( EpgProgramTests )
    unittest.TextTestRunner( verbosity=2 ).run( suite )
