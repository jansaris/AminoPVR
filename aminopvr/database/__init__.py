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

from aminopvr.database import db
import logging

_logger = logging.getLogger( "aminopvr.database" )

class MainSanityCheck( db.DbSanityCheck ):
    def check( self ):
        pass
 
# def backupDatabase(version):
#     helpers.backupVersionedFile(db.dbFilename(), version)

# ======================
# = Main DB Migrations =
# ======================
# Add new migrations at the bottom of the list; subclass the previous migration.


class InitialSchema( db.SchemaUpgrade ):
    def test(self):
        return self.checkDbVersion() >= 1

    def execute(self):
        queries = [
                   """CREATE TABLE epg_ids ( 
                                               epg_id   TEXT PRIMARY KEY
                                                             NOT NULL,
                                               strategy TEXT NOT NULL 
                                           );""",
                   """CREATE TABLE schedules ( 
                                                 id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                                                 type               INTEGER,
                                                 channel_id         INTEGER,
                                                 start_time         INTEGER,
                                                 end_time           INTEGER,
                                                 title              TEXT,
                                                 prefer_hd          INTEGER,
                                                 prefer_unscrambled INTEGER,
                                                 dup_method         INTEGER,
                                                 start_early        INTEGER,
                                                 end_late           INTEGER,
                                                 inactive           INTEGER 
                                             );""",
                   """CREATE TABLE genres ( 
                                              id    INTEGER PRIMARY KEY AUTOINCREMENT
                                                            NOT NULL,
                                              genre TEXT    NOT NULL
                                                            UNIQUE 
                                          );""",
                   """CREATE TABLE persons ( 
                                               id     INTEGER PRIMARY KEY AUTOINCREMENT
                                                              NOT NULL,
                                               person TEXT    NOT NULL
                                                              UNIQUE 
                                           );""",
                   """CREATE TABLE recording_program_actors ( 
                                                                program_id INTEGER NOT NULL,
                                                                person_id  INTEGER NOT NULL,
                                                                PRIMARY KEY ( program_id, person_id ) 
                                                            );""",
                   """CREATE TABLE recording_program_directors ( 
                                                                   program_id INTEGER NOT NULL,
                                                                   person_id  INTEGER NOT NULL,
                                                                   PRIMARY KEY ( program_id, person_id ) 
                                                               );""",
                   """CREATE TABLE recording_program_genres ( 
                                                                program_id INTEGER NOT NULL,
                                                                genre_id   INTEGER NOT NULL,
                                                                PRIMARY KEY ( program_id, genre_id ) 
                                                            );""",
                   """CREATE TABLE recording_program_presenters ( 
                                                                    program_id INTEGER NOT NULL,
                                                                    person_id  INTEGER NOT NULL,
                                                                    PRIMARY KEY ( program_id, person_id ) 
                                                                );""",
                   """CREATE TABLE epg_program_presenters ( 
                                                              program_id INTEGER NOT NULL,
                                                              person_id  INTEGER NOT NULL,
                                                              PRIMARY KEY ( program_id, person_id ) 
                                                          );""",
                   """CREATE TABLE epg_program_genres ( 
                                                          program_id INTEGER NOT NULL,
                                                          genre_id   INTEGER NOT NULL,
                                                          PRIMARY KEY ( program_id, genre_id ) 
                                                      );""",
                   """CREATE TABLE epg_program_actors ( 
                                                          program_id INTEGER NOT NULL,
                                                          person_id  INTEGER NOT NULL,
                                                          PRIMARY KEY ( program_id, person_id ) 
                                                      );""",
                   """CREATE TABLE epg_programs ( 
                                                    epg_id          TEXT    NOT NULL,
                                                    id              INTEGER PRIMARY KEY AUTOINCREMENT
                                                                            NOT NULL,
                                                    original_id     TEXT    NOT NULL
                                                                            UNIQUE,
                                                    start_time      INTEGER NOT NULL,
                                                    end_time        INTEGER NOT NULL,
                                                    title           TEXT    NOT NULL,
                                                    subtitle        TEXT    NOT NULL,
                                                    description     TEXT    NOT NULL,
                                                    aspect_ratio    TEXT    NOT NULL,
                                                    parental_rating TEXT    NOT NULL,
                                                    ratings         TEXT    NOT NULL,
                                                    detailed        INTEGER NOT NULL 
                                                );""",
                   """CREATE TABLE recording_programs ( 
                                                          epg_id          TEXT    NOT NULL,
                                                          id              INTEGER PRIMARY KEY AUTOINCREMENT
                                                                                  NOT NULL,
                                                          original_id     TEXT    NOT NULL
                                                                                  UNIQUE,
                                                          start_time      INTEGER NOT NULL,
                                                          end_time        INTEGER NOT NULL,
                                                          title           TEXT    NOT NULL,
                                                          subtitle        TEXT    NOT NULL,
                                                          description     TEXT    NOT NULL,
                                                          aspect_ratio    TEXT    NOT NULL,
                                                          parental_rating TEXT    NOT NULL,
                                                          ratings         TEXT    NOT NULL,
                                                          detailed        INTEGER NOT NULL 
                                                      );""",
                   """CREATE TABLE epg_program_directors ( 
                                                             program_id INTEGER NOT NULL,
                                                             person_id  INTEGER NOT NULL,
                                                             PRIMARY KEY ( program_id, person_id ) 
                                                         );""",
                   """CREATE TABLE channel_urls ( 
                                                    channel_id INTEGER NOT NULL,
                                                    type       TEXT    NOT NULL,
                                                    protocol   TEXT    NOT NULL,
                                                    ip         TEXT    NOT NULL,
                                                    port       INTEGER NOT NULL,
                                                    arguments  TEXT    NOT NULL,
                                                    scrambled  INTEGER NOT NULL,
                                                    PRIMARY KEY ( channel_id, type ) 
                                                );""",
                   """CREATE TABLE pending_channel_urls ( 
                                                            channel_id INTEGER NOT NULL,
                                                            type       TEXT    NOT NULL,
                                                            protocol   TEXT    NOT NULL,
                                                            ip         TEXT    NOT NULL,
                                                            port       INTEGER NOT NULL,
                                                            arguments  TEXT    NOT NULL,
                                                            scrambled  INTEGER NOT NULL,
                                                            PRIMARY KEY ( channel_id, type ) 
                                                        );""",
                   """CREATE TABLE pending_channels ( 
                                                        id         INTEGER PRIMARY KEY AUTOINCREMENT
                                                                           NOT NULL,
                                                        number     INTEGER NOT NULL,
                                                        epg_id     TEXT    NOT NULL,
                                                        name       TEXT    NOT NULL,
                                                        name_short TEXT    NOT NULL,
                                                        logo       TEXT    NOT NULL,
                                                        thumbnail  TEXT    NOT NULL,
                                                        radio      INTEGER NOT NULL
                                                                           DEFAULT '0',
                                                        inactive   INTEGER NOT NULL
                                                                           DEFAULT ( 0 ) 
                                                    );""",
                   """CREATE TABLE channels ( 
                                                id         INTEGER PRIMARY KEY AUTOINCREMENT
                                                                   NOT NULL,
                                                number     INTEGER NOT NULL,
                                                epg_id     TEXT    NOT NULL,
                                                name       TEXT    NOT NULL,
                                                name_short TEXT    NOT NULL,
                                                logo       TEXT    NOT NULL,
                                                thumbnail  TEXT    NOT NULL,
                                                radio      INTEGER NOT NULL
                                                                   DEFAULT '0',
                                                inactive   INTEGER NOT NULL
                                                                   DEFAULT ( 0 ) 
                                            );""",
                   """CREATE TABLE old_recordings ( 
                                                      id               INTEGER PRIMARY KEY AUTOINCREMENT
                                                                               NOT NULL,
                                                      schedule_id      INTEGER NOT NULL,
                                                      epg_program_id   INTEGER NOT NULL,
                                                      channel_id       INTEGER NOT NULL,
                                                      channel_name     TEXT    NOT NULL,
                                                      channel_url_type TEXT    NOT NULL,
                                                      start_time       INTEGER NOT NULL,
                                                      end_time         INTEGER NOT NULL,
                                                      length           INTEGER NOT NULL,
                                                      title            TEXT    NOT NULL,
                                                      filename         TEXT    NOT NULL
                                                                               UNIQUE,
                                                      file_size        INTEGER NOT NULL,
                                                      stream_arguments TEXT    NOT NULL,
                                                      marker           INTEGER NOT NULL,
                                                      type             TEXT    NOT NULL,
                                                      scrambled        INTEGER NOT NULL,
                                                      status           INTEGER NOT NULL,
                                                      rerecord         INTEGER NOT NULL,
                                                      UNIQUE ( channel_id, start_time, end_time ) 
                                                  );""",
                   """CREATE TABLE glashart_pages ( 
                                                      page    TEXT PRIMARY KEY,
                                                      content TEXT 
                                                  );""",
                   """CREATE TABLE glashart_page_symbols ( 
                                                             [key] TEXT PRIMARY KEY,
                                                             value TEXT 
                                                         );""",
                   """CREATE TABLE recordings ( 
                                                  id               INTEGER PRIMARY KEY AUTOINCREMENT
                                                                           NOT NULL,
                                                  schedule_id      INTEGER NOT NULL,
                                                  epg_program_id   INTEGER NOT NULL,
                                                  channel_id       INTEGER NOT NULL,
                                                  channel_name     TEXT    NOT NULL,
                                                  channel_url_type TEXT    NOT NULL,
                                                  start_time       INTEGER NOT NULL,
                                                  end_time         INTEGER NOT NULL,
                                                  length           INTEGER NOT NULL,
                                                  title            TEXT    NOT NULL,
                                                  filename         TEXT    NOT NULL
                                                                           UNIQUE,
                                                  file_size        INTEGER NOT NULL,
                                                  stream_arguments TEXT    NOT NULL,
                                                  marker           INTEGER NOT NULL,
                                                  type             TEXT    NOT NULL,
                                                  scrambled        INTEGER NOT NULL,
                                                  status           INTEGER NOT NULL,
                                                  rerecord         INTEGER NOT NULL,
                                                  UNIQUE ( channel_id, start_time, end_time ) 
                                              );""",
                   """CREATE TABLE db_version ( 
                                                  db_version INTEGER 
                                              );""",
                   """CREATE INDEX epg_programs_epg_id ON epg_programs ( 
                                                                           epg_id 
                                                                       );""",
                   """CREATE INDEX epg_programs_start_time ON epg_programs ( 
                                                                               start_time ASC 
                                                                           );""",
                   """CREATE INDEX epg_programs_end_time ON epg_programs ( 
                                                                             end_time ASC 
                                                                         );""",
                   """INSERT INTO db_version (db_version) VALUES (0);"""
        ]

        self.connection.delayCommit( True )
        for query in queries:
            self.connection.execute( query )
        self.connection.delayCommit( False )

        self.incDbVersion()

        # cleanup and reduce db if any previous data was removed
        #self.connection.execute( "VACUUM" )
