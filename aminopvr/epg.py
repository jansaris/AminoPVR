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
from aminopvr.db import DBConnection
from aminopvr.tools import getTimestamp, printTraceback
import channel
import copy
import logging
import sys

class EpgId( object ):
    _logger = logging.getLogger( 'aminopvr.EPG.EpgId' )

    def __init__( self, epgId, strategy ):
        self._epgId    = unicode( epgId )
        self._strategy = unicode( strategy )
        self._channels = []

    def __hash__( self ):
        return hash( hash( self._epgId ) + hash( self._strategy ) )

    def __repr__( self ):
        return "EpgId( epgId=%r, strategy=%r )" % ( self._epgId, self._strategy )

    def __eq__( self, other ):
        return ( self._epgId    == other._epgId    and
                 self._strategy == other._strategy )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @property
    def epgId( self ):
        return self._epgId

    @property
    def strategy( self ):
        return self._strategy

    @strategy.setter
    def strategy( self, strategy ):
        self._strategy = unicode( strategy )

    @classmethod
    def getAllFromDb( cls, conn, includeRadio=False ):
        epgids = []
        if conn:
            rows = conn.execute( "SELECT * FROM epg_ids" )
            for row in rows:
                channels = channel.Channel.getAllByEpgIdFromDb( conn, row["epg_id"], includeRadio=includeRadio )
                if len( channels ) > 0:
                    epgid           = cls( row["epg_id"], row["strategy"] )
                    epgid._channels = channels
                    epgids.append( epgid )
                else:
                    cls._logger.info( "getAllFromDb: no channels for epgId=%s" % ( row["epg_id"] ) )

        epgidsSorted = sorted( epgids, key=lambda k: k._channels[0]._number ) 

        return epgidsSorted

    @classmethod
    def getFromDb( cls, conn, epgId ):
        epgid = None
        if conn:
            row = conn.execute( "SELECT * FROM epg_ids WHERE epg_id=?", ( epgId, ) )
            if row:
                epgid = cls( row[0]["epg_id"], row[0]["strategy"] )

        return epgid

    def addToDb( self, conn ):
        if conn:
            epgId = EpgId.getFromDb( conn, self._epgId )
            if epgId:
                if self != epgId:
                    conn.execute( "UPDATE epg_ids SET strategy=? WHERE epg_id=?", ( self._strategy, self._epgId ) )
            else:
                conn.insert( "INSERT INTO epg_ids (epg_id, strategy) VALUES (?, ?)", ( self._epgId, self._strategy ) )

    def deleteFromDb( self, conn ):
        if conn:
            conn.execute( "DELETE FROM epg_ids WHERE epg_id=?", ( self._epgId, ) )

    def dump( self ):
        return ( "%s: %s" % ( self._epgId, self._strategy ) )

#Adult
#Animated
#Arts/Culture
#Art/Music
#Children
#Comedy
#Crime/Mystery
#Documentary
#Drama
#Educational
#Film
#Music
#News
#Religion
#Science/Nature
#Sports
#Talk
#Unknown

class Genre( object ):
    _logger     = logging.getLogger( 'aminopvr.Genre' )

    _genreCache = {}

    def __init__( self, id=-1 ):    # @ReservedAssignment
        self._id     = int( id )
        self._genre  = ""

    def __hash__( self ):
        return hash( self._genre )

    def __repr__( self ):
        return "Genre( id=%r, genre=%r )" % ( self._id, self._genre )

    def __eq__( self, other ):
        # Not comparing _id as it might not be set at comparison time.
        # For insert/update descision it is not relevant
        if not other:
            return False
        assert isinstance( other, Genre ), "Other object not instance of class Genre: %r" % ( other )
        return ( self._genre == other._genre )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @property
    def id( self ):
        return self._id

    @property
    def genre( self ):
        return self._genre

    @genre.setter
    def genre( self, genre ):
        self._genre = unicode( genre )

    @classmethod
    def getFromDb( cls, conn, id ): # @ReservedAssignment
        genre = None
        if id in cls._genreCache:
            genre = cls._genreCache[id]
        else:
            if conn:
                row = conn.execute( "SELECT * FROM genres WHERE id=?", ( id, ) )
                if row:
                    genre = cls._createGenreFromDbDict( row[0] )
                    cls._genreCache[id] = genre

        return genre

    @classmethod
    def getAllFromDb( cls, conn ):
        genres = []
        if conn:
            rows = conn.execute( "SELECT * FROM genres" )
            genres = [ cls._createGenreFromDbDict( row ) for row in rows if row ]

        return genres

    @classmethod
    def getByGenreFromDb( cls, conn, genre ):
        dbGenre = None
        if conn:
            row = conn.execute( "SELECT * FROM genres WHERE genre=?", ( genre, ) )
            if row:
                dbGenre = cls._createGenreFromDbDict( row[0] )

        return dbGenre

    @classmethod
    def _createGenreFromDbDict( cls, genreData ):
        genre = None
        if genreData:
            try:
                genre       = cls( genreData["id"] )
                genre.genre = genreData["genre"]

                if genre._id not in cls._genreCache:
                    cls._genreCache[genre._id] = genre
            except:
                cls._logger.error( "_createGenreFromDbDict: unexpected error: %s" % ( sys.exc_info()[0] ) )
                printTraceback()
        return genre

    def addToDb( self, conn ):
        if conn:
            if self._id == -1:
                if self._genre != "":
                    dbGenre = Genre.getByGenreFromDb( conn, self._genre )
                    if not dbGenre:
                        conn.insert( "INSERT INTO genres (genre) VALUES (?)", ( self._genre, ) )
                        dbGenre = Genre.getByGenreFromDb( conn, self._genre )
                    self._id = dbGenre._id
                else:
                    self._logger.warning( "Genre.addToDb: self._genre is empty" );

        return self._id

    def dump( self ):
        return ( "%s" % ( repr( self._genre ) ) )

class Person( object ):
    _logger = logging.getLogger( 'aminopvr.Person' )

    _personCache = {}

    def __init__( self, id=-1 ):   # @ReservedAssignment
        self._id     = int( id )
        self._person = ""

    def __hash__( self ):
        return hash( self._person )

    def __repr__( self ):
        return "Person( id=%r, person=%r )" % ( self._id, self._person )

    def __eq__( self, other ):
        if not other:
            return False
        assert isinstance( other, Person ), "Other object not instance of class Person: %r" % ( other )
        return ( self._person == other._person )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @property
    def id( self ):
        return self._id

    @property
    def person( self ):
        return self._person

    @person.setter
    def person( self, person ):
        self._person = unicode( person )

    @classmethod
    def getFromDb( cls, conn, id ): # @ReservedAssignment
        person = None
        if id in cls._personCache:
            person = cls._personCache[id]
        else:
            if conn:
                row = conn.execute( "SELECT * FROM persons WHERE id=?", ( id, ) )
                if row:
                    person = cls._createPersonFromDbDict( row[0] )

        return person

    @classmethod
    def getAllFromDb( cls, conn ):
        persons = []
        if conn:
            rows    = conn.execute( "SELECT * FROM persons" )
            persons = [ cls._createPersonFromDbDict( row ) for row in rows if row ]

        return persons

    @classmethod
    def getByPersonFromDB( cls, conn, person ):
        dbPerson = None
        if conn:
            row = conn.execute( "SELECT * FROM persons WHERE person=?", ( person, ) )
            if row:
                dbPerson = cls._createPersonFromDbDict( row[0] )

        return dbPerson

    @classmethod
    def _createPersonFromDbDict( cls, personData ):
        person = None
        if personData:
            try:
                person        = cls( personData["id"] )
                person.person = personData["person"]

                if person._id not in cls._personCache:
                    cls._personCache[person._id] = person
            except:
                cls._logger.error( "_createPersonFromDbDict: unexpected error: %s" % ( sys.exc_info()[0] ) )
                printTraceback()
        return person


    def addToDb( self, conn ):
        if conn:
            if self._id == -1:
                if self._person != "":
                    dbPerson = self.getByPersonFromDB( conn, self._person )
                    if not dbPerson:
                        conn.insert( "INSERT INTO persons (person) VALUES (?)", ( self._person, ) )
                        dbPerson = self.getByPersonFromDB( conn, self._person )
                    self._id = dbPerson._id
                else:
                    self._logger.warning( "Person.addToDb: self._person is empty" );

        return self._id

    def dump( self ):
        return ( "%s" % ( repr( self._person ) ) )

class ProgramGenreAbstract( object ):
    _tableName = None

    def __init__( self, programId=-1, genreId=-1 ):
        self._programId = int( programId )
        self._genreId   = int( genreId )
        self._genre     = Genre()

    def __hash__( self ):
        return hash( hash( self._programId ) + hash( self._genreId ) )

    def __repr__( self ):
        return "ProgramGenreAbstract( programId=%r, genreId=%r, genre=%r )" % ( self._programId, self._genreId, self._genre )

    def __eq__( self, other ):
        if not other:
            return False
        assert isinstance( other, ProgramGenreAbstract ), "Other object not instance of class ProgramGenreAbstract: %r" % ( other )
        return ( self._programId == other._programId and
                 self._genreId   == other._genreId )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @classmethod
    def copy( cls, programGenre ):
        if isinstance( programGenre, ProgramGenreAbstract ):
            programGenre = copy.copy( programGenre )
            programGenre.__class__  = cls
            programGenre._programId = -1
            return programGenre
        return None

    @property
    def programId( self ):
        return self._programId

    @programId.setter
    def programId( self, programId ):
        if self._programId == -1:
            self._programId = int( programId )
        else:
            self._logger.critical( "ProgramGenreAbstract.programId: programId is already != -1, so cannot be changed! self._programId=%d, programId=%d" % ( self._programId, int( programId ) ) )

    @property
    def genreId( self ):
        return self._genreId

    @genreId.setter
    def genreId( self, genreId ):
        if self._genreId == -1:
            self._genreId = int( genreId )
        else:
            self._logger.critical( "ProgramGenreAbstract.genreId: genreId is already != -1, so cannot be changed! self._genreId=%d, genreId=%d" % ( self._genreId, int( genreId ) ) )

    @property
    def genre( self ):
        assert self._genre, "Genre not set"
        return self._genre

    @genre.setter
    def genre( self, genre ):
        self._genre = genre
        if genre:
            if not isinstance( genre, Genre ):
                assert False, "ProgramGenreAbstract.genre: genre not a Genre instance: %r" % ( genre )
                self._genre   = None
                self._genreId = -1
            else:
                self._genreId = genre.id

    @classmethod
    def getFromDb( cls, conn, programId, genreId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programGenre = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE program_id=? AND genre_id=?" % ( cls._tableName ), ( programId, genreId ) )
            if row:
                programGenre = cls._createProgramGenreFromDbDict( conn, row[0] )

        return programGenre

    @classmethod
    def getAllFromDb( cls, conn, programId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programGenres = []
        if conn:
            rows          = conn.execute( "SELECT * FROM %s WHERE program_id=?" % ( cls._tableName ), ( programId, ) )
            programGenres = [ cls._createProgramGenreFromDbDict( conn, row ) for row in rows if row ]

        return programGenres

    @classmethod
    def _createProgramGenreFromDbDict( cls, conn, programGenreData ):
        programGenre = None
        if programGenreData:
            try:
                programGenre = cls( programGenreData["program_id"], programGenreData["genre_id"] )
                genre        = Genre.getFromDb( conn, programGenreData["genre_id"] )
                if genre:
                    programGenre.genre = genre
                else:
                    cls._logger.warning( "_createProgramGenreFromDbDict: Genre with id %s not in database." % ( programGenreData["genre_id"] ) )
            except:
                cls._logger.error( "_createProgramGenreFromDbDict: unexpected error: %s" % ( sys.exc_info()[0] ) )
                printTraceback()
        return programGenre

    def addToDb( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if self._programId == -1:
            self._logger.error( "ProgramGenreAbstract.addToDb: programId is not valid" )
            return
        if conn:
            genreId = self._genre.addToDb( conn )
            if self._genreId == -1:
                self._genreId = genreId

            programGenre = self.getFromDb( conn, self._programId, self._genreId )
            if not programGenre:
                conn.insert( "INSERT INTO %s (program_id, genre_id) VALUES (?, ?)" % ( self._tableName ), ( self._programId, self._genreId ) )

    @classmethod
    def deleteByProgramIdFromDb( cls, conn, programId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        if conn:
            conn.execute( "DELETE FROM %s WHERE program_id=?" % ( cls._tableName ), ( programId, ) )

    def deleteFromDb( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
            conn.execute( "DELETE FROM %s WHERE program_id=? AND genre_id=?" % ( self._tableName ), ( self._programId, self._genreId ) )

    def dump( self ):
        return self._genre.dump()

class EpgProgramGenre( ProgramGenreAbstract ):
    _tableName = "epg_program_genres"
    _logger    = logging.getLogger( 'aminopvr.EPG.ProgramGenre' )

class RecordingProgramGenre( ProgramGenreAbstract ):
    _tableName = "recording_program_genres"
    _logger    = logging.getLogger( 'aminopvr.Recording.ProgramGenre' )

class ProgramPersonAbstract( object ):
    _tableName  = None

    def __init__( self, programId=-1, personId=-1 ):
        self._programId = int( programId )
        self._personId  = int( personId )
        self._person    = Person()

    def __hash__( self ):
        return hash( hash( self._programId ) + hash( self._personId ) )

    def __repr__( self ):
        return "ProgramPersonAbstract( programId=%r, personId=%r, person=%r )" % ( self._programId, self._personId, self._person )

    def __eq__( self, other ):
        if not other:
            return False
        assert isinstance( other, ProgramPersonAbstract ), "Other object not instance of class ProgramPersonAbstract: %r" % ( other )
        return ( self._programId == other._programId and
                 self._personId  == other._personId )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @classmethod
    def copy( cls, programPerson ):
        if isinstance( programPerson, ProgramPersonAbstract ):
            programPerson = copy.copy( programPerson )
            programPerson.__class__  = cls
            programPerson._programId = -1
            return programPerson
        return None

    @property
    def programId( self ):
        return self._programId

    @programId.setter
    def programId( self, programId ):
        if self._programId == -1:
            self._programId = int( programId )
        else:
            self._logger.critical( "ProgramPersonAbstract.programId: programId is already != -1, so cannot be changed! self._programId=%d, programId=%d" % ( self._programId, int( programId ) ) )

    @property
    def personId( self ):
        return self._personId

    @personId.setter
    def personId( self, personId ):
        if self._personId == -1:
            self._personId = int( personId )
        else:
            self._logger.critical( "ProgramPersonAbstract.personId: personId is already != -1, so cannot be changed! self._personId=%d, personId=%d" % ( self._personId, int( personId ) ) )

    @property
    def person( self ):
        assert self._person, "Person not set"
        return self._person

    @person.setter
    def person( self, person ):
        self._person = person
        if person:
            if not isinstance( person, Person ):
                assert False, "ProgramPersonAbstract.person: person not a Person instance: %r" % ( person )
                self._person   = None
                self._personId = -1
            else:
                self._personId = person.id

    @classmethod
    def getFromDb( cls, conn, programId, personId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programPerson = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE program_id=? AND person_id=?" % ( cls._tableName ), ( programId, personId ) )
            if row:
                programPerson = cls._createProgramPersonFromDbDict( conn, row[0] )

        return programPerson

    @classmethod
    def getAllFromDb( cls, conn, programId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programPersons = []
        if conn:
            rows           = conn.execute( "SELECT * FROM %s WHERE program_id=?" % ( cls._tableName ), ( programId, ) )
            programPersons = [ cls._createProgramPersonFromDbDict( conn, row ) for row in rows if row ]

        return programPersons

    @classmethod
    def _createProgramPersonFromDbDict( cls, conn, programPersonData ):
        programPerson = None
        if programPersonData:
            try:
                programPerson = cls( programPersonData["program_id"], programPersonData["person_id"] )
                person        = Person.getFromDb( conn, programPersonData["person_id"] )
                if person:
                    programPerson.person = person
                else:
                    cls._logger.warning( "_createProgramPersonFromDbDict: Person with id %s not in database." % ( programPersonData["person_id"] ) )
            except:
                cls._logger.error( "_createProgramPersonFromDbDict: unexpected error: %s" % ( sys.exc_info()[0] ) )
                printTraceback()
        return programPerson

    def addToDb( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if self._programId == -1:
            self._logger.error( "ProgramPersonAbstract.addToDb: programId is not valid" )
            return
        if conn:
            personId = self._person.addToDb( conn )
            if self._personId == -1:
                self._personId = personId

            programPerson = self.getFromDb( conn, self._programId, self._personId )
            if not programPerson:
                conn.insert( "INSERT INTO %s (program_id, person_id) VALUES (?, ?)" % ( self._tableName ), ( self._programId, self._personId ) )

    @classmethod
    def deleteByProgramIdFromDb( cls, conn, programId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        if conn:
            conn.execute( "DELETE FROM %s WHERE program_id=?" % ( cls._tableName ), ( programId, ) )

    def deleteFromDb( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
            conn.execute( "DELETE FROM %s WHERE program_id=? AND person_id=?" % ( self._tableName ), ( self._programId, self._personId ) )

    def dump( self ):
        return self._person.dump()

class EpgProgramDirector( ProgramPersonAbstract ):
    _tableName = "epg_program_directors"
    _logger    = logging.getLogger( 'aminopvr.EPG.ProgramDirector' )

class RecordingProgramDirector( ProgramPersonAbstract ):
    _tableName = "recording_program_directors"
    _logger    = logging.getLogger( 'aminopvr.Recording.ProgramDirector' )

class EpgProgramActor( ProgramPersonAbstract ):
    _tableName = "epg_program_actors"
    _logger    = logging.getLogger( 'aminopvr.EPG.ProgramActor' )

class RecordingProgramActor( ProgramPersonAbstract ):
    _tableName = "recording_program_actors"
    _logger    = logging.getLogger( 'aminopvr.Recording.ProgramActor' )

class EpgProgramPresenter( ProgramPersonAbstract ):
    _tableName = "epg_program_presenters"
    _logger    = logging.getLogger( 'aminopvr.EPG.ProgramPresenter' )

class RecordingProgramPresenter( ProgramPersonAbstract ):
    _tableName = "recording_program_presenters"
    _logger    = logging.getLogger( 'aminopvr.Recording.ProgramPresenter' )

class ProgramAbstract( object ):

    SEARCH_TITLE       = 1
    SEARCH_SUBTITLE    = 2
    SEARCH_DESCRIPTION = 4

    _tableName      = None

    def __init__( self, id=-1 ):    # @ReservedAssignment
        self._id             = int( id )
        self._epgId          = "epgid1"
        self._originalId     = ""
        self._startTime      = 0
        self._endTime        = 0
        self._title          = "Program 1"
        self._subtitle       = ""
        self._description    = ""
        self._aspectRatio    = ""
        self._parentalRating = ""
        self._genres         = []
        self._actors         = []
        self._directors      = []
        self._presenters     = []
        self._ratings        = []
        self._detailed       = False

    def __hash__( self ):
        return ( hash( hash( self._epgId ) +
                       hash( self._originalId ) +
                       hash( self._startTime ) +
                       hash( self._endTime ) +
                       hash( self._title ) +
                       hash( self._detailed ) +
                       hash( self._subtitle ) +
                       hash( self._description ) +
                       hash( self._aspectRatio ) +
                       hash( self._parentalRating ) +
                       hash( frozenset( self._genres ) ) +
                       hash( frozenset( self._actors ) ) +
                       hash( frozenset( self._directors ) ) +
                       hash( frozenset( self._presenters ) ) +
                       hash( frozenset( self._ratings ) ) ) )

    def __repr__( self ):
        return "ProgramAbstract( epgId=%r, id=%r, originalId=%r, startTime=%r, endTime=%r, title=%r, subtitle=%r, description=%r, aspectRatio=%r, parentalRating=%r, genres=%r, actors=%r, directors=%r, presenters=%r, ratings=%r )" % ( self._epgId, self._id, self._originalId, self._startTime, self._endTime, self._title, self._subtitle, self._description, self._aspectRatio, self._parentalRating, self._genres, self._actors, self._directors, self._presenters, self._ratings )

    def __eq__( self, other ):
        # Not comparing _id as it might not be set at comparison time.
        # For insert/update descision it is not relevant
        if not other:
            return False
        assert isinstance( other, ProgramAbstract ), "Other object not instance of class ProgramAbstract: %r" % ( other )
        return ( self._epgId                                            == other._epgId            and
                 self._originalId                                       == other._originalId       and
                 self._startTime                                        == other._startTime        and
                 self._endTime                                          == other._endTime          and
                 self._title                                            == other._title            and
                 self._detailed                                         == other._detailed         and
                 self._subtitle                                         == other._subtitle         and
                 self._description                                      == other._description      and
                 self._aspectRatio                                      == other._aspectRatio      and
                 self._parentalRating                                   == other._parentalRating   and
                 ( set( self._genres     ) & set( other._genres     ) ) == set( self._genres )     and
                 ( set( self._actors     ) & set( other._actors     ) ) == set( self._actors )     and
                 ( set( self._directors  ) & set( other._directors  ) ) == set( self._directors )  and
                 ( set( self._presenters ) & set( other._presenters ) ) == set( self._presenters ) and
                 ( set( self._ratings    ) & set( other._ratings    ) ) == set( self._ratings ) )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @classmethod
    def copy( cls, program ):
        if isinstance( program, ProgramAbstract ):
            program = copy.copy( program )
            program.__class__ = cls
            program._id       = -1
            return program
        return None

    @property
    def id( self ):
        return self._id

    @id.setter
    def id( self, id ): # @ReservedAssignment
        if self._id == -1:
            self._id = int( id )
        else:
            self._logger.critical( "ProgramAbstract.id: id is already != -1, so cannot be changed! self._id=%d, id=%d" % ( self._id, int( id ) ) )

    @property
    def epgId( self ):
        return self._epgId

    @epgId.setter
    def epgId( self, epgId ):
        self._epgId = unicode( epgId )

    @property
    def originalId( self ):
        return self._originalId

    @originalId.setter
    def originalId( self, originalId ):
        self._originalId = unicode( originalId )

    @property
    def startTime( self ):
        return self._startTime

    @startTime.setter
    def startTime( self, startTime ):
        self._startTime = int( startTime )

    @property
    def endTime( self ):
        return self._endTime

    @endTime.setter
    def endTime( self, endTime ):
        self._endTime = int( endTime )

    @property
    def title( self ):
        return self._title

    @title.setter
    def title( self, title ):
        self._title = unicode( title )

    @property
    def subtitle( self ):
        return self._subtitle

    @subtitle.setter
    def subtitle( self, subtitle ):
        self._subtitle = unicode( subtitle )

    @property
    def description( self ):
        return self._description

    @description.setter
    def description( self, description ):
        self._description = unicode( description )

    @property
    def aspectRatio( self ):
        return self._aspectRatio

    @aspectRatio.setter
    def aspectRatio( self, aspectRatio ):
        self._aspectRatio = unicode( aspectRatio )

    @property
    def parentalRating( self ):
        return self._parentalRating

    @parentalRating.setter
    def parentalRating( self, parentalRating ):
        self._parentalRating = unicode( parentalRating )

    @property
    def detailed( self ):
        return self._detailed

    @detailed.setter
    def detailed( self, detailed ):
        self._detailed = int( detailed )

    @property
    def genres( self ):
        return self._genres

    @genres.setter
    def genres( self, genres ):
        self._genres = genres

    @property
    def actors( self ):
        return self._actors

    @actors.setter
    def actors( self, actors ):
        self._actors = actors

    @property
    def directors( self ):
        return self._directors

    @directors.setter
    def directors( self, directors ):
        self._directors = directors

    @property
    def presenters( self ):
        return self._presenters

    @presenters.setter
    def presenters( self, presenters ):
        self._presenters = presenters

    @property
    def ratings( self ):
        return self._ratings

    @ratings.setter
    def ratings( self, ratings ):
        self._ratings = ratings

    @classmethod
    def getAllFromDb( cls, conn, startTime = None ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programs = []
        if conn:
            rows = None
            if startTime == None:
                rows = conn.execute( "SELECT * FROM %s ORDER BY epg_id ASC, start_time ASC" % ( cls._tableName ) )
            else:
                rows = conn.execute( "SELECT * FROM %s WHERE end_time > ? ORDER BY epg_id ASC, start_time ASC" % ( cls._tableName ), ( startTime, ) )
            programs = [ cls._createProgramFromDbDict( conn, row ) for row in rows if row ]

        return programs

    @classmethod
    def getAllByEpgIdFromDb( cls, conn, epgId, startTime=None, endTime=None ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programs = []
        if conn:
            rows = None
            if startTime == None:
                if endTime == None:
                    rows = conn.execute( "SELECT * FROM %s WHERE epg_id=? ORDER BY start_time ASC"  % ( cls._tableName ), ( epgId, ) )
                else:
                    rows = conn.execute( "SELECT * FROM %s WHERE epg_id=? AND start_time < ? ORDER BY start_time ASC"  % ( cls._tableName ), ( epgId, endTime, ) )
            else:
                if endTime == None:
                    rows = conn.execute( "SELECT * FROM %s WHERE epg_id=? AND end_time > ? ORDER BY start_time ASC" % ( cls._tableName ), ( epgId, startTime ) )
                else:
                    rows = conn.execute( "SELECT * FROM %s WHERE epg_id=? AND end_time > ? AND start_time < ? ORDER BY start_time ASC" % ( cls._tableName ), ( epgId, startTime, endTime ) )
            programs = [ cls._createProgramFromDbDict( conn, row ) for row in rows ]

        return programs

    @classmethod
    def getByOriginalIdFromDb( cls, conn, originalId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        program = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE original_id=?" % ( cls._tableName ), ( originalId, ) )
            if row:
                program = cls._createProgramFromDbDict( conn, row[0] )

        return program

    @classmethod
    def getFromDb( cls, conn, id ): # @ReservedAssignment
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        program = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE id=?" % ( cls._tableName ), ( id, ) )
            if row:
                program = cls._createProgramFromDbDict( conn, row[0] )

        return program

    @classmethod
    def getByTitleFromDb( cls, conn, title, epgId=None, startTime=None, searchWhere=SEARCH_TITLE ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programs = []
        if conn:
            where       = []
            whereValue  = []
            search      = []
            title       = '%' + title + '%'

            if epgId:
                where.append( "epg_id = ?" )
                whereValue.append( epgId )

            if startTime:
                where.append( "start_time > ?" )
                whereValue.append( startTime )

            if searchWhere & ProgramAbstract.SEARCH_TITLE:
                search.append( "title LIKE ?" )
                whereValue.append( title )
            elif searchWhere & ProgramAbstract.SEARCH_SUBTITLE:
                search.append( "subtitle LIKE ?" )
                whereValue.append( title )
            elif searchWhere & ProgramAbstract.SEARCH_DESCRIPTION:
                search.append( "description LIKE ?" )
                whereValue.append( title )

            where.append( "(" + " OR ".join( search ) + ")" )
            query    = "SELECT * FROM %s WHERE " % ( cls._tableName ) + " AND ".join( where ) + " ORDER BY start_time ASC"
            rows     = conn.execute( query, whereValue )
            programs = [ cls._createProgramFromDbDict( conn, row ) for row in rows ]
        return programs

    @classmethod
    def getNowNextFromDb( cls, conn ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programs = []
        if conn:
            now      = getTimestamp()
            query    = "SELECT t2.* FROM %s t1 LEFT JOIN %s t2 ON ( t1.epg_id=t2.epg_id AND (t2.start_time=t1.end_time OR t2.start_time=t1.start_time) ) WHERE t1.start_time <= ? AND t1.end_time > ? ORDER BY t2.epg_id ASC, t2.start_time ASC, t2.end_time ASC;" % ( cls._tableName, cls._tableName )
            rows     = conn.execute( query, [ now, now ] )
            programs = [ cls._createProgramFromDbDict( conn, row ) for row in rows ]
        return programs

    def deleteFromDb( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
            conn.execute( "DELETE FROM %s WHERE id=?" % ( self._tableName ), ( self._id, ) )
            for genre in self._genres:
                genre.deleteFromDb( conn )
            for actor in self._actors:
                actor.deleteFromDb( conn )
            for director in self._directors:
                director.deleteFromDb( conn )
            for presenter in self._presenters:
                presenter.deleteFromDb( conn )

    def toDict( self ):
        epgProgramDict = { "epg_id":     self._epgId,
                           "id":         self._id,
                           "title":      self._title,
                           "start_time": self._startTime,
                           "end_time":   self._endTime }

        # To reduce size of json object / dictionary, only add following elements when they're set
        if self._subtitle != "":
            epgProgramDict["subtitle"]        = self._subtitle
        if self._description != "":
            epgProgramDict["description"]     = self._description
        if len( self._genres ) > 0:
            epgProgramDict["genres"]          = [ genre.genre.genre       for genre     in self._genres     if genre ]
        if len( self._actors ) > 0:
            epgProgramDict["actors"]          = [ actor.person.person     for actor     in self._actors     if actor ]
        if len( self._directors ) > 0:
            epgProgramDict["directors"]       = [ director.person.person  for director  in self._directors  if director ]
        if len( self._presenters ) > 0:
            epgProgramDict["presenters"]      = [ presenter.person.person for presenter in self._presenters if presenter ]
        if len( self._ratings ) > 0:
            epgProgramDict["ratings"]         = self._ratings
        if self._aspectRatio != "":
            epgProgramDict["aspect_ratio"]    = self._aspectRatio
        if self._parentalRating != "":
            epgProgramDict["parental_rating"] = self._parentalRating

        return epgProgramDict

    def dump( self ):
        genres     = [ genre.dump()     for genre     in self._genres ];
        actors     = [ actor.dump()     for actor     in self._actors ];
        directors  = [ director.dump()  for director  in self._directors ];
        presenters = [ presenter.dump() for presenter in self._presenters ];
        return ( "%s - %i (%s): %s, %i, %i, %s, %s, %s, [%s], [%s], [%s], [%s]" % ( self._tableName, self._id, self._originalId, self._epgId, self._startTime, self._endTime, repr( self._title ), repr( self._subtitle ), repr( self._description ), ", ".join( genres ), ", ".join( actors ), ", ".join( directors ), ", ".join( presenters ) ) )

class EpgProgram( ProgramAbstract ):
    _tableName = "epg_programs"
    _logger    = logging.getLogger( 'aminopvr.EPG.Program' )

    @classmethod
    def _createProgramFromDbDict( cls, conn, programData ):
        program = None
        if programData:
            try:
                program                 = EpgProgram( programData["id"] )
                program.epgId           = programData["epg_id"]
                program.originalId      = programData["original_id"]
                program.startTime       = programData["start_time"]
                program.endTime         = programData["end_time"]
                program.title           = programData["title"]
                program.subtitle        = programData["subtitle"]
                program.description     = programData["description"]
                program.aspectRatio     = programData["aspect_ratio"]
                program.parentalRating  = programData["parental_rating"]
                program.detailed        = programData["detailed"]
                program.genres          = EpgProgramGenre.getAllFromDb( conn, programData["id"] )
                program.actors          = EpgProgramActor.getAllFromDb( conn, programData["id"] )
                program.directors       = EpgProgramDirector.getAllFromDb( conn, programData["id"] )
                program.presenters      = EpgProgramPresenter.getAllFromDb( conn, programData["id"] )
                if programData["ratings"] != "":
                    program.ratings     = programData["ratings"].split( ";" )
            except:
                cls._logger.error( "_createProgramFromDbDict: unexpected error: %s" % ( sys.exc_info()[0] ) )
                printTraceback()
                program = None
        return program

    @classmethod
    def getTimestampLastProgram( cls, conn ):
        timestamp = 0
        if conn:
            rows = conn.execute( "SELECT MAX( end_time ) AS end_time FROM epg_programs" )
            if len( rows ) == 1:
                timestamp = rows[0]["end_time"]
        return timestamp

    @classmethod
    def deleteByTimeFromDB( cls, conn, startTime ):
        if conn:
            conn.execute( "DELETE FROM epg_program_genres WHERE program_id IN (SELECT id FROM epg_programs WHERE end_time < ?)", ( startTime, ) )
            conn.execute( "DELETE FROM epg_program_actors WHERE program_id IN (SELECT id FROM epg_programs WHERE end_time < ?)", ( startTime, ) )
            conn.execute( "DELETE FROM epg_program_directors WHERE program_id IN (SELECT id FROM epg_programs WHERE end_time < ?)", ( startTime, ) )
            conn.execute( "DELETE FROM epg_program_presenters WHERE program_id IN (SELECT id FROM epg_programs WHERE end_time < ?)", ( startTime, ) )
            conn.execute( "DELETE FROM epg_programs WHERE end_time < ?", ( startTime, ) )

    def addToDb( self, conn ):
        if conn:
#             # This shouldn't really happen, because the EpgProvider should have already made sure there are
#             # no duplicate originalIds. Moreover, originalId is specific to the EpgProvider used (e.g. Glashart)
#             # and might not be unique (TODO: check db structure!).
#             # Also, this generates a query for each new EpgProgram, which is expensive.
#             if self._id == -1:
#                 program = self.getByOriginalIdFromDb( conn, self._originalId )
#                 if program:
#                     self._logger.warning( "addToDb: We didn't know id, but there seems to be a program with the same originalId (id=%d, originalId=%s)" % ( program._id, self._originalId ) )
#                     self._id = program._id

            if self._id != -1:
                conn.execute( """
                                 UPDATE
                                     epg_programs
                                 SET
                                     epg_id=?,
                                     original_id=?,
                                     start_time=?,
                                     end_time=?,
                                     title=?,
                                     subtitle=?,
                                     description=?,
                                     aspect_ratio=?,
                                     parental_rating=?,
                                     ratings=?,
                                     detailed=?
                                 WHERE
                                     id=?
                              """, ( self._epgId,
                                     self._originalId,
                                     self._startTime,
                                     self._endTime,
                                     self._title,
                                     self._subtitle,
                                     self._description,
                                     self._aspectRatio,
                                     self._parentalRating,
                                     ";".join( self._ratings ),
                                     self._detailed,
                                     self._id ) )
            else:
                programId = conn.insert( """
                                            INSERT INTO
                                                epg_programs (epg_id,
                                                              original_id,
                                                              start_time,
                                                              end_time,
                                                              title,
                                                              subtitle,
                                                              description,
                                                              aspect_ratio,
                                                              parental_rating,
                                                              ratings,
                                                              detailed)
                                            VALUES
                                                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                         """, ( self._epgId,
                                                self._originalId,
                                                self._startTime,
                                                self._endTime,
                                                self._title,
                                                self._subtitle,
                                                self._description,
                                                self._aspectRatio,
                                                self._parentalRating,
                                                ";".join( self._ratings ),
                                                self._detailed ) )
                if programId:
                    self._id = programId
                else:
                    self._logger.error( "Inserted row, but no auto-increment id returned!" )

            if self._id != -1:
                # Delete programs of the same channel but with different IDs when:
                # - the start and end time completely overlap
                # - the start time overlaps and the end time is after the program being added.
                conn.execute( """
                                 DELETE FROM
                                     epg_program_genres
                                 WHERE
                                     program_id IN ( SELECT
                                                         id
                                                     FROM
                                                         epg_programs
                                                     WHERE
                                                         epg_id = ? AND
                                                         id != ?    AND
                                                         ( ( start_time >= ? AND
                                                             end_time <= ? ) OR
                                                           ( start_time >= ? AND
                                                             start_time < ?  AND
                                                             end_time > ? ) ) )
                              """, ( self._epgId,
                                     self._id,
                                     self._startTime,
                                     self._endTime,
                                     self._startTime,
                                     self._endTime,
                                     self._endTime ) )
                conn.execute( """
                                 DELETE FROM
                                     epg_program_actors
                                 WHERE
                                     program_id IN ( SELECT
                                                         id
                                                     FROM
                                                         epg_programs
                                                     WHERE
                                                         epg_id = ? AND
                                                         id != ?    AND
                                                         ( ( start_time >= ? AND
                                                             end_time <= ? ) OR
                                                           ( start_time >= ? AND
                                                             start_time < ?  AND
                                                             end_time > ? ) ) )
                              """, ( self._epgId,
                                     self._id,
                                     self._startTime,
                                     self._endTime,
                                     self._startTime,
                                     self._endTime,
                                     self._endTime ) )
                conn.execute( """
                                 DELETE FROM
                                     epg_program_directors
                                 WHERE
                                     program_id IN ( SELECT
                                                         id
                                                     FROM
                                                         epg_programs
                                                     WHERE
                                                         epg_id = ? AND
                                                         id != ?    AND
                                                         ( ( start_time >= ? AND
                                                             end_time <= ? ) OR
                                                           ( start_time >= ? AND
                                                             start_time < ?  AND
                                                             end_time > ? ) ) )
                              """, ( self._epgId,
                                     self._id,
                                     self._startTime,
                                     self._endTime,
                                     self._startTime,
                                     self._endTime,
                                     self._endTime ) )
                conn.execute( """
                                 DELETE FROM
                                     epg_program_presenters
                                 WHERE
                                     program_id IN ( SELECT
                                                         id
                                                     FROM
                                                         epg_programs
                                                     WHERE
                                                         epg_id = ? AND
                                                         id != ?    AND
                                                         ( ( start_time >= ? AND
                                                             end_time <= ? ) OR
                                                           ( start_time >= ? AND
                                                             start_time < ?  AND
                                                             end_time > ? ) ) )
                              """, ( self._epgId,
                                     self._id,
                                     self._startTime,
                                     self._endTime,
                                     self._startTime,
                                     self._endTime,
                                     self._endTime ) )
                conn.execute( """
                                 DELETE FROM
                                     epg_programs
                                 WHERE
                                     epg_id = ? AND
                                     id != ?    AND
                                     ( ( start_time >= ? AND
                                         end_time <= ? ) OR
                                       ( start_time >= ? AND
                                         start_time < ?  AND
                                         end_time > ? ) )
                              """, ( self._epgId,
                                     self._id,
                                     self._startTime,
                                     self._endTime,
                                     self._startTime,
                                     self._endTime,
                                     self._endTime ) )

                for genre in self._genres:
                    genre.programId = self._id
                for actor in self._actors:
                    actor.programId = self._id
                for director in self._directors:
                    director.programId = self._id
                for presenter in self._presenters:
                    presenter.programId = self._id

                genres            = EpgProgramGenre.getAllFromDb( conn, self._id )
                actors            = EpgProgramActor.getAllFromDb( conn, self._id )
                directors         = EpgProgramDirector.getAllFromDb( conn, self._id )
                presenters        = EpgProgramPresenter.getAllFromDb( conn, self._id )
                removedGenres     = set( genres ).difference( set( self._genres ) )
                newGenres         = set( self._genres ).difference( set( genres ) )
                removedActors     = set( actors ).difference( set( self._actors ) )
                newActors         = set( self._actors ).difference( set( actors ) )
                removedDirectors  = set( directors ).difference( set( self._directors ) )
                newDirectors      = set( self._directors ).difference( set( directors ) )
                removedPresenters = set( presenters ).difference( set( self._presenters ) )
                newPresenters     = set( self._presenters ).difference( set( presenters ) )
                for genre in removedGenres:
                    genre.deleteFromDb( conn )
                for genre in newGenres:
                    genre.addToDb( conn )
                for actor in removedActors:
                    actor.deleteFromDb( conn )
                for actor in newActors:
                    actor.addToDb( conn )
                for director in removedDirectors:
                    director.deleteFromDb( conn )
                for director in newDirectors:
                    director.addToDb( conn )
                for presenter in removedPresenters:
                    presenter.deleteFromDb( conn )
                for presenter in newPresenters:
                    presenter.addToDb( conn )

class RecordingProgram( ProgramAbstract ):
    _tableName = "recording_programs"
    _logger    = logging.getLogger( 'aminopvr.Recording.Program' )

    @classmethod
    def copy( cls, program ):
        program = super( RecordingProgram, cls ).copy( program )
        genres     = []
        actors     = []
        directors  = []
        presenters = []
        for genre in program.genres:
            genres.append( RecordingProgramGenre.copy( genre ) )
        for actor in program.actors:
            actors.append( RecordingProgramActor.copy( actor ) )
        for directory in program.directors:
            directors.append( RecordingProgramDirector.copy( directory ) )
        for presenter in program.presenters:
            presenters.append( RecordingProgramPresenter.copy( presenter ) )
        program.genres     = genres
        program.actors     = actors
        program.directors  = directors
        program.presenters = presenters
        return program

    @classmethod
    def _createProgramFromDbDict( cls, conn, programData ):
        program = None
        if programData:
            try:
                program                 = RecordingProgram( programData["id"] )
                program.epgId           = programData["epg_id"]
                program.originalId      = programData["original_id"]
                program.startTime       = programData["start_time"]
                program.endTime         = programData["end_time"]
                program.title           = programData["title"]
                program.subtitle        = programData["subtitle"]
                program.description     = programData["description"]
                program.aspectRatio     = programData["aspect_ratio"]
                program.parentalRating  = programData["parental_rating"]
                program.detailed        = programData["detailed"]
                program.genres          = RecordingProgramGenre.getAllFromDb( conn, programData["id"] )
                program.actors          = RecordingProgramActor.getAllFromDb( conn, programData["id"] )
                program.directors       = RecordingProgramDirector.getAllFromDb( conn, programData["id"] )
                program.presenters      = RecordingProgramPresenter.getAllFromDb( conn, programData["id"] )
                if programData["ratings"] != "":
                    program.ratings     = programData["ratings"].split( ";" )
            except:
                cls._logger.error( "_createProgramFromDbDict: unexpected error: %s" % ( sys.exc_info()[0] ) )
                printTraceback()
                program = None

        return program

    def addToDb( self, conn ):
        if conn:
#             program = None
#             # TODO: is this really necessery? If _id != -1, then we simply update the database, no matter if it has
#             # changed or not. If properly tested, updating does not change state of object. 
#             if self._id != -1:
#                 program = self.getFromDb( conn, self._id )
#                 if not program:
#                     self._logger.warning( "addToDb: We expected to find a program, but didn't. (id=%d)" % ( self._id ) )
#                     self._id = -1

            if self._id != -1:
                conn.execute( """
                                 UPDATE
                                     recording_programs
                                 SET
                                     epg_id=?,
                                     original_id=?,
                                     start_time=?,
                                     end_time=?,
                                     title=?,
                                     subtitle=?,
                                     description=?,
                                     aspect_ratio=?,
                                     parental_rating=?,
                                     ratings=?,
                                     detailed=?
                                 WHERE
                                     id=?
                              """, ( self._epgId,
                                     self._originalId,
                                     self._startTime,
                                     self._endTime,
                                     self._title,
                                     self._subtitle,
                                     self._description,
                                     self._aspectRatio,
                                     self._parentalRating,
                                     ";".join( self._ratings ),
                                     self._detailed,
                                     self._id ) )
            else:
                programId = conn.insert( """
                                            INSERT INTO
                                                recording_programs (epg_id,
                                                                    original_id,
                                                                    start_time,
                                                                    end_time,
                                                                    title,
                                                                    subtitle,
                                                                    description,
                                                                    aspect_ratio,
                                                                    parental_rating,
                                                                    ratings,
                                                                    detailed)
                                            VALUES
                                                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                         """, ( self._epgId,
                                                self._originalId,
                                                self._startTime,
                                                self._endTime,
                                                self._title,
                                                self._subtitle,
                                                self._description,
                                                self._aspectRatio,
                                                self._parentalRating,
                                                ";".join( self._ratings ),
                                                self._detailed ) )
                if programId:
                    self._id = programId
                else:
                    self._logger.error( "Inserted row, but no auto-increment id returned!" )

            if self._id != -1:
                for genre in self._genres:
                    genre.programId = self._id
                for actor in self._actors:
                    actor.programId = self._id
                for director in self._directors:
                    director.programId = self._id
                for presenter in self._presenters:
                    presenter.programId = self._id

                genres            = RecordingProgramGenre.getAllFromDb( conn, self._id )
                actors            = RecordingProgramActor.getAllFromDb( conn, self._id )
                directors         = RecordingProgramDirector.getAllFromDb( conn, self._id )
                presenters        = RecordingProgramPresenter.getAllFromDb( conn, self._id )
                removedGenres     = set( genres ).difference( self._genres )
                newGenres         = set( self._genres ).difference( genres )
                removedActors     = set( actors ).difference( self._actors )
                newActors         = set( self._actors ).difference( actors )
                removedDirectors  = set( directors ).difference( self._directors )
                newDirectors      = set( self._directors ).difference( directors )
                removedPresenters = set( presenters ).difference( self._presenters )
                newPresenters     = set( self._presenters ).difference( presenters )
                for genre in removedGenres:
                    genre.deleteFromDb( conn )
                for genre in newGenres:
                    genre.addToDb( conn )
                for actor in removedActors:
                    actor.deleteFromDb( conn )
                for actor in newActors:
                    actor.addToDb( conn )
                for director in removedDirectors:
                    director.deleteFromDb( conn )
                for director in newDirectors:
                    director.addToDb( conn )
                for presenter in removedPresenters:
                    presenter.deleteFromDb( conn )
                for presenter in newPresenters:
                    presenter.addToDb( conn )

def main():
    sys.stderr.write( "main()\n" );

    conn = DBConnection()
    if conn:
        programs = EpgProgram.getByTitleFromDb( conn, "de", searchWhere=EpgProgram.SEARCH_TITLE | EpgProgram.SEARCH_SUBTITLE | EpgProgram.SEARCH_DESCRIPTION )
        for program in programs:
            sys.stderr.write( program.dump() + "\n" )

        program = EpgProgram.getFromDb( conn, 1 )
        sys.stderr.write( "%s\n" % ( program.dump() ) )
        for genre in program.genres:
            sys.stderr.write( "genre: %r\n" % ( genre ) )
        for actor in program.actors:
            sys.stderr.write( "actor: %r\n" % ( actor ) )
        for director in program.directors:
            sys.stderr.write( "directory: %r\n" % ( director ) )
        for presenter in program.presenters:
            sys.stderr.write( "presenter: %r\n" % ( presenter ) )
        recordingProgram = RecordingProgram.copy( program )
        sys.stderr.write( "%s\n" % ( recordingProgram.dump() ) )
        for genre in recordingProgram.genres:
            sys.stderr.write( "genre: %r\n" % ( genre ) )
        for actor in recordingProgram.actors:
            sys.stderr.write( "actor: %r\n" % ( actor ) )
        for director in recordingProgram.directors:
            sys.stderr.write( "directory: %r\n" % ( director ) )
        for presenter in recordingProgram.presenters:
            sys.stderr.write( "presenter: %r\n" % ( presenter ) )

# allow this to be a module
if __name__ == '__main__':
    main()
