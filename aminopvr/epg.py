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
import channel
import copy
import logging
import sys

class EpgId( object ):
    _logger   = None

    def __init__( self, epgId, strategy ):
        self._epgId    = unicode( epgId )
        self._strategy = unicode( strategy )
        self._channels = []

        self._logger   = logging.getLogger( 'aminopvr.EPG.EpgId' )

    def __hash__( self ):
        return hash( self._epgId ) + hash( self._strategy )

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
            rows = conn.execute( "SELECT * FROM epg_ids" ).fetchall()
            for row in rows:
                channels = channel.Channel.getAllByEpgIdFromDb( conn, row["epg_id"], includeRadio )
                if len( channels ) > 0:
                    epgid           = cls( row["epg_id"], row["strategy"] )
                    epgid._channels = channels
                    epgids.append( epgid )

        epgidsSorted = sorted( epgids, key=lambda k: k._channels[0]._number ) 

        return epgidsSorted

    @classmethod
    def getFromDb( cls, conn, epgID ):
        epgid = None
        if conn:
            row = conn.execute( "SELECT * FROM epg_ids WHERE epg_id=?", ( epgID, ) ).fetchone()
            if row:
                epgid = cls( row["epg_id"], row["strategy"] )

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
            conn.execute( "DELETE FROM %s WHERE epg_id=?" % ( self._tableName ), ( self._epgId ) )

#    def getConfigEntry( self ):
#        channels = ""
#        for channel in self._channels:
#            if channels != "":
#                channels = channels + ", "
#            channels = channels + channel.name
#        return ( "%s %s %s\n" % ( self._epgId, self._strategy, filter_line( channels ) ) )


    def dump( self ):
        return ( "%s: %s" % ( self._epgId, self._strategy ) )

class Genre( object ):
    _logger    = logging.getLogger( 'aminopvr.Genre' )

    def __init__( self, id, genre ):
        self._id     = id
        self._genre  = unicode( genre )

    def __hash__( self ):
        return hash( self._genre )

    def __repr__( self ):
        return "Genre( id=%r, genre=%r )" % ( self._id, self._genre )

    def __eq__( self, other ):
        # Not comparng _id as it might not be set at comparison time.
        # For insert/update descision it is not relevant
        return ( self._genre == other._genre )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @property
    def genre( self ):
        return self._genre

    @classmethod
    def getFromDb( cls, conn, id ):
        genre = None
        if conn:
            row = conn.execute( "SELECT * FROM genres WHERE id=?", ( id, ) ).fetchone()
            if row:
                genre = cls( row["id"], row["genre"] )

        return genre

    @classmethod
    def getAllFromDb( cls, conn ):
        genres = []
        if conn:
            rows = conn.execute( "SELECT * FROM genres" ).fetchall()
            for row in rows:
                genres.append( cls( row["id"], row["genre"] ) )

        return genres

    @classmethod
    def getByGenreFromDb( cls, conn, genre ):
        dbGenre = None
        if conn:
            row = conn.execute( "SELECT * FROM genres WHERE genre=?", ( genre, ) ).fetchone()
            if row:
                dbGenre = cls( row["id"], row["genre"] )

        return dbGenre

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

    def __init__( self, id, person ):
        self._id     = id
        self._person = unicode( person )

    def __hash__( self ):
        return hash( self._person )

    def __repr__( self ):
        return "Person( id=%r, person=%r )" % ( self._id, self._person )

    def __eq__( self, other ):
        return ( self._person == other._person )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @classmethod
    def getFromDb( cls, conn, id ):
        person = None
        if conn:
            row = conn.execute( "SELECT * FROM persons WHERE id=?", ( id, ) ).fetchone()
            if row:
                person = cls( row["id"], row["person"] )

        return person

    @classmethod
    def getAllFromDb( cls, conn ):
        persons = []
        if conn:
            rows = conn.execute( "SELECT * FROM persons" ).fetchall()
            for row in rows:
                persons.append( cls( row["id"], row["person"] ) )

        return persons

    @classmethod
    def getByPersonFromDB( cls, conn, person ):
        dbPerson = None
        if conn:
            row = conn.execute( "SELECT * FROM persons WHERE person=?", ( person, ) ).fetchone()
            if row:
                dbPerson = cls( row["id"], row["person"] )

        return dbPerson

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

    def __init__( self, programId, genreId, genre = Genre( -1, "" ) ):
        self._programId = programId
        self._genreId   = genreId
        self._genre     = genre

    def __hash__( self ):
        return hash( self._programId ) + hash( self._genreId )

    def __repr__( self ):
        return "ProgramGenreAbstract( programId=%r, genreId=%r, genre=%r )" % ( self._programId, self._genreId, self._genre )

    def __eq__( self, other ):
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
        self._programId = programId

    @property
    def genreId( self ):
        return self._genreId

    @genreId.setter
    def genreId( self, genreId ):
        self._genreId = genreId

    @classmethod
    def getFromDb( cls, conn, programId, genreId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programGenre = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE program_id=? AND genre_id=?" % ( cls._tableName ), ( programId, genreId ) ).fetchone()
            if row:
                genre = Genre.getFromDb( conn, row["genre_id"] )
                if genre:
                    programGenre = cls( row["program_id"], row["genre_id"], genre )
                else:
                    cls._logger.warning( "ProgramGenreAbstract.getFromDb: Genre with id %s not in database." % ( row["genre_id"] ) )
                    programGenre = cls( row["program_id"], row["genre_id"] )

        return programGenre

    @classmethod
    def getAllFromDb( cls, conn, programId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programGenres = []
        if conn:
            rows = conn.execute( "SELECT * FROM %s WHERE program_id=?" % ( cls._tableName ), ( programId, ) ).fetchall()
            for row in rows:
                genre = Genre.getFromDb( conn, row["genre_id"] )
                if genre:
                    programGenres.append( cls( row["program_id"], row["genre_id"], genre ) )
                else:
                    cls._logger.warning( "ProgramGenreAbstract.getFromDb: Genre with id %s not in database." % ( row["genre_id"] ) )
                    programGenres.append( cls( row["program_id"], row["genre_id"] ) )

        return programGenres

    def addToDb( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
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

    def __init__( self, programId, personId, person = Person( -1, "" ) ):
        self._programId = programId
        self._personId  = personId
        self._person    = person

    def __hash__( self ):
        return hash( self._programId ) + hash( self._personId )

    def __repr__( self ):
        return "ProgramPersonAbstract( programId=%r, personId=%r, person=%r )" % ( self._programId, self._personId, self._person )

    def __eq__( self, other ):
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
        self._programId = programId

    @property
    def personId( self ):
        return self._personId

    @personId.setter
    def personId( self, personId ):
        self._personId = personId

    @classmethod
    def getFromDb( cls, conn, programId, personId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programPerson = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE program_id=? AND person_id=?" % ( cls._tableName ), ( programId, personId ) ).fetchone()
            if row:
                person = Person.getFromDb( conn, row["person_id"] )
                if person:
                    programPerson = cls( row["program_id"], row["person_id"], person )
                else:
                    cls._logger.warning( "ProgramPersonAbstract.getFromDb: Person with id %s not in database." % ( row["person_id"] ) )
                    programPerson = cls( row["program_id"], row["person_id"] )

        return programPerson

    @classmethod
    def getAllFromDb( cls, conn, programId ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programPersons = []
        if conn:
            rows = conn.execute( "SELECT * FROM %s WHERE program_id=?" % ( cls._tableName ), ( programId, ) ).fetchall()
            for row in rows:
                person = Person.getFromDb( conn, row["person_id"] )
                if person:
                    programPersons.append( cls( row["program_id"], row["person_id"], person ) )
                else:
                    cls._logger.warning( "ProgramPersonAbstract.getFromDb: Person with id %s not in database." % ( row["person_id"] ) )
                    programPersons.append( cls( row["program_id"], row["person_id"] ) )

        return programPersons

    def addToDb( self, conn ):
        assert self._tableName != None, "Not the right class: %r" % ( self )
        if conn:
            personId = self._person.addToDb( conn )
            if self._personId == -1:
                self._personId = personId

            programDirector = self.getFromDb( conn, self._programId, self._personId )
            if not programDirector:
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

    def __init__( self, epgId, id, originalId, startTime, endTime, title, subtitle="", description="", aspectRatio="", parentalRating="", detailed=False ):
        self._epgId          = unicode( epgId )
        self._id             = id
        self._originalId     = unicode( originalId )
        self._startTime      = startTime
        self._endTime        = endTime
        self._title          = unicode( title )
        self._subtitle       = unicode( subtitle )
        self._description    = unicode( description )
        self._aspectRatio    = unicode( aspectRatio )
        self._parentalRating = unicode( parentalRating )
        self._genres         = []
        self._actors         = []
        self._directors      = []
        self._presenters     = []
        self._ratings        = []
        self._detailed       = detailed

    def __hash__( self ):
        return ( hash( self._epgId + self._originalId + self._title + self._subtitle + self._description ) +
                 hash( self._startTime + self._endTime ) + hash( self._aspectRatio + self._parentalRating ) +
                 hash( self._genres + self._actors + self._directors + self._presenters + self._ratings ) )

    def __repr__( self ):
        return "ProgramGenreAbstract( epgId=%r, id=%r, originalId=%r, startTime=%r, endTime=%r, title=%r, subtitle=%r, description=%r, aspectRatio=%r, parentalRating=%r, genres=%r, actors=%r, directors=%r, presenters=%r, ratings=%r )" % ( self._epgId, self._id, self._originalId, self._startTime, self._endTime, self._title, self._subtitle, self._description, self._aspectRatio, self._parentalRating, self._genres, self._actors, self._directors, self._presenters, self._ratings )

    def __eq__( self, other ):
        # Not comparng _id as it might not be set at comparison time.
        # For insert/update descision it is not relevant
        return ( self._epgId                                                      == other._epgId            and
                 self._originalId                                                 == other._originalId       and
                 self._startTime                                                  == other._startTime        and
                 self._endTime                                                    == other._endTime          and
                 self._title                                                      == other._title            and
                 self._subtitle                                                   == other._subtitle         and
                 self._description                                                == other._description      and
                 self._aspectRatio                                                == other._aspectRatio      and
                 self._parentalRating                                             == other._parentalRating   and
                 self._detailed                                                   == other._detailed         and
                 set( self._genres     ).intersection( set( other._genres     ) ) == set( self._genres )     and
                 set( self._actors     ).intersection( set( other._actors     ) ) == set( self._actors )     and
                 set( self._directors  ).intersection( set( other._directors  ) ) == set( self._directors )  and
                 set( self._presenters ).intersection( set( other._presenters ) ) == set( self._presenters ) and
                 set( self._ratings    ).intersection( set( other._ratings    ) ) == set( self._ratings ) )

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

    @property
    def epgId( self ):
        return self._epgId

    @property
    def originalId( self ):
        return self._originalId

    @property
    def startTime( self ):
        return self._startTime

    @startTime.setter
    def startTime( self, startTime ):
        self._startTime = startTime

    @property
    def endTime( self ):
        return self._endTime

    @endTime.setter
    def endTime( self, endTime ):
        self._endTime = endTime

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
        self._detailed = detailed

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
                rows = conn.execute( "SELECT * FROM %s ORDER BY epg_id ASC, start_time ASC" % ( cls._tableName ) ).fetchall()
            else:
                rows = conn.execute( "SELECT * FROM %s WHERE end_time > ? ORDER BY epg_id ASC, start_time ASC" % ( cls._tableName ), ( startTime, ) ).fetchall()
            for row in rows:
                program = cls._createProgramFromDbDict( conn, row )
                programs.append( program )

        return programs

    @classmethod
    def getAllByEpgIdFromDb( cls, conn, epgId, startTime = None ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programs = []
        if conn:
            rows = None
            if startTime == None:
                rows = conn.execute( "SELECT * FROM %s WHERE epg_id=? ORDER BY start_time ASC"  % ( cls._tableName ), ( epgId, ) ).fetchall()
            else:
                rows = conn.execute( "SELECT * FROM %s WHERE epg_id=? AND end_time > ? ORDER BY start_time ASC" % ( cls._tableName ), ( epgId, startTime ) ).fetchall()
            for row in rows:
                program = cls._createProgramFromDbDict( conn, row )
                programs.append( program )

        return programs

    @classmethod
    def getFromDb( cls, conn, id ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        program = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE id=?" % ( cls._tableName ), ( id, ) ).fetchone()
            program = cls._createProgramFromDbDict( conn, row )

        return program

    @classmethod
    def getByTitleFromDb( cls, conn, title, epgId=None, startTime=None, searchWhere=SEARCH_TITLE ):
        assert cls._tableName != None, "Not the right class: %r" % ( cls )
        programs = []
        if conn:
            where       = []
            whereValue  = []
            search      = []

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
            query = "SELECT * FROM %s WHERE " % ( cls._tableName ) + " AND ".join( where )
            rows = conn.execute( query, whereValue ).fetchall()
            for row in rows:
                program = cls._createProgramFromDbDict( conn, row )
                programs.append( program )
        return programs


    def dump( self ):
        genres     = [];
        actors     = [];
        directors  = [];
        presenters = [];
        for genre in self._genres:
            genres.append( genre.dump() )
        for actor in self._actors:
            actors.append( actor.dump() )
        for director in self._directors:
            directors.append( director.dump() )
        for presenter in self._presenters:
            presenters.append( presenter.dump() )
        return ( "%s - %i: %s, %i, %i, %s, %s, %s, [%s], [%s], [%s], [%s]" % ( self._tableName, self._id, self._epgId, self._startTime, self._endTime, repr( self._title ), repr( self._subtitle ), repr( self._description ), ", ".join( genres ), ", ".join( actors ), ", ".join( directors ), ", ".join( presenters ) ) )

class EpgProgram( ProgramAbstract ):
    _tableName = "epg_programs"
    _logger    = logging.getLogger( 'aminopvr.EPG.Program' )

    @classmethod
    def getByOriginalIdFromDb( cls, conn, originalId ):
        program = None
        if conn:
            row = conn.execute( "SELECT * FROM %s WHERE original_id=?" % ( cls._tableName ), ( originalId, ) ).fetchone()
            program = cls._createProgramFromDbDict( conn, row )

        return program

    @classmethod
    def _createProgramFromDbDict( cls, conn, programData ):
        program = None
        if programData:
            program            = EpgProgram( programData["epg_id"], programData["id"], programData["original_id"], programData["start_time"], programData["end_time"], programData["title"], programData["subtitle"], programData["description"], programData["aspect_ratio"], programData["parental_rating"], programData["detailed"] )
            program.genres     = EpgProgramGenre.getAllFromDb( conn, programData["id"] )
            program.actors     = EpgProgramActor.getAllFromDb( conn, programData["id"] )
            program.directors  = EpgProgramDirector.getAllFromDb( conn, programData["id"] )
            program.presenters = EpgProgramPresenter.getAllFromDb( conn, programData["id"] )
            if programData["ratings"] != "":
                program.ratings = programData["ratings"].split( ";" )
        return program

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
            program = None
            if self._id != -1:
                program = self.getFromDb( conn, self._id )
                if not program:
                    self._id = -1

            if self._id == -1:
                program = self.getByOriginalIdFromDb( conn, self._originalId )
                if program:
                    self._id = program._id

            if self._id != -1:
                if program and self != program:
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
                id = conn.insert( """
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
                if id:
                    self._id = id
                    for genre in self._genres:
                        genre.programId = id
                    for actor in self._actors:
                        actor.programId = id
                    for director in self._directors:
                        director.programId = id
                    for presenter in self._presenters:
                        presenter.programId = id

            if self.id != -1:
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
            program            = RecordingProgram( programData["epg_id"], programData["id"], programData["original_id"], programData["start_time"], programData["end_time"], programData["title"], programData["subtitle"], programData["description"], programData["aspect_ratio"], programData["parental_rating"], programData["detailed"] )
            program.genres     = RecordingProgramGenre.getAllFromDb( conn, programData["id"] )
            program.actors     = RecordingProgramActor.getAllFromDb( conn, programData["id"] )
            program.directors  = RecordingProgramDirector.getAllFromDb( conn, programData["id"] )
            program.presenters = RecordingProgramPresenter.getAllFromDb( conn, programData["id"] )
            if programData["ratings"] != "":
                program.ratings = programData["ratings"].split( ";" )
        return program

    def addToDb( self, conn ):
        if conn:
            program = None
            if self._id != -1:
                program = self.getFromDb( conn, self._id )
                if not program:
                    self._id = -1

            if self._id == -1:
                program = self.getByOriginalIdFromDb( conn, self._originalId )
                if program:
                    self._id = program._id

            if self._id != -1:
                if program and self != program:
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
                id = conn.insert( """
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
                if id:
                    self._id = id
                    for genre in self._genres:
                        genre.programId = id
                    for actor in self._actors:
                        actor.programId = id
                    for director in self._directors:
                        director.programId = id
                    for presenter in self._presenters:
                        presenter.programId = id

            if self._id != -1:
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
