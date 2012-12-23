-- Table: channels
DROP TABLE IF EXISTS channels;
CREATE TABLE channels ( 
    id         INTEGER PRIMARY KEY AUTOINCREMENT
                       NOT NULL,
    number     INTEGER NOT NULL,
    epg_id     TEXT    NOT NULL,
    name       TEXT    NOT NULL,
    name_short TEXT    NOT NULL,
    logo       TEXT    NOT NULL,
    thumbnail  TEXT    NOT NULL,
    radio      INTEGER NOT NULL
                       DEFAULT 0
);




-- Table: channel_urls
DROP TABLE IF EXISTS channel_urls;
CREATE TABLE channel_urls ( 
    channel_id INTEGER NOT NULL,
    type       TEXT    NOT NULL,
    protocol   TEXT    NOT NULL,
    ip         TEXT    NOT NULL,
    port       INTEGER NOT NULL,
    arguments  TEXT    NOT NULL,
    PRIMARY KEY ( channel_id, type ) 
);



-- Table: epg_genres
DROP TABLE IF EXISTS epg_genres;
CREATE TABLE epg_genres (
    id         INTEGER PRIMARY KEY AUTOINCREMENT
                       NOT NULL,
    genre      TEXT    UNIQUE
                       NOT NULL
);


-- Table: epg_ids
DROP TABLE IF EXISTS epg_ids;
CREATE TABLE epg_ids (
    epg_id     TEXT PRIMARY KEY
                    NOT NULL,
    strategy   TEXT NOT NULL
);


-- Table: epg_persons
DROP TABLE IF EXISTS epg_persons;
CREATE TABLE epg_persons (
    id         INTEGER PRIMARY KEY AUTOINCREMENT
                       NOT NULL,
    person     TEXT    UNIQUE
                       NOT NULL
);


-- Table: epg_programs
DROP TABLE IF EXISTS epg_programs;
CREATE TABLE epg_programs (
    epg_id          TEXT    NOT NULL,
    id              TEXT    PRIMARY KEY
                            NOT NULL,
    start_time      INTEGER NOT NULL,
    end_time        INTEGER NOT NULL,
    title           TEXT    NOT NULL,
    subtitle        TEXT    NOT NULL,
    description     TEXT    NOT NULL,
    aspect_ratio    TEXT    NOT NULL,
    parental_rating TEXT    NOT NULL,
    ratings         TEXT    NOT NULL,
    detailed        INTEGER NOT NULL
);

DROP INDEX IF EXISTS epg_programs_epg_id;
DROP INDEX IF EXISTS epg_programs_start_time;
DROP INDEX IF EXISTS epg_programs_end_time;
CREATE INDEX epg_programs_epg_id     ON epg_programs ( epg_id );
CREATE INDEX epg_programs_start_time ON epg_programs ( start_time ASC );
CREATE INDEX epg_programs_end_time   ON epg_programs ( end_time   ASC );

-- Table: epg_program_actors
DROP TABLE IF EXISTS epg_program_actors;
CREATE TABLE epg_program_actors (
    id          TEXT    NOT NULL,
    actor_id    INTEGER NOT NULL,
    PRIMARY KEY ( id, actor_id )
);

DROP INDEX IF EXISTS epg_program_actors_id;
CREATE INDEX epg_program_actors_id ON epg_program_actors ( id );

-- Table: epg_program_directors
DROP TABLE IF EXISTS epg_program_directors;
CREATE TABLE epg_program_directors (
    id          TEXT    NOT NULL,
    director_id INTEGER NOT NULL,
    PRIMARY KEY ( id, director_id )
);

DROP INDEX IF EXISTS epg_program_directors_id;
CREATE INDEX epg_program_directors_id ON epg_program_directors ( id );

-- Table: epg_program_genres
DROP TABLE IF EXISTS epg_program_genres;
CREATE TABLE epg_program_genres (
    id          TEXT    NOT NULL,
    genre_id    INTEGER NOT NULL,
    PRIMARY KEY ( id, genre_id )
);

DROP INDEX IF EXISTS epg_program_genres_id;
CREATE INDEX epg_program_genres_id ON epg_program_genres ( id );

-- Table: epg_program_presenters
DROP TABLE IF EXISTS epg_program_presenters;
CREATE TABLE epg_program_presenters (
    id              TEXT    NOT NULL,
    presenter_id    INTEGER NOT NULL,
    PRIMARY KEY ( id, presenter_id )
);

DROP INDEX IF EXISTS epg_program_presenters_id;
CREATE INDEX epg_program_presenters_id ON epg_program_presenters ( id );

-- Table: recordings
DROP TABLE IF EXISTS recordings;
CREATE TABLE recordings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT
                        NOT NULL,
    channel_id  INTEGER NOT NULL,
    start_time  INTEGER NOT NULL,
    end_time    INTEGER NOT NULL,
    title       TEXT    NOT NULL,
    subtitle    TEXT    NOT NULL,
    description TEXT    NOT NULL,
    filename    TEXT    UNIQUE
                        NOT NULL,
    marker      INTEGER NOT NULL,
    UNIQUE ( channel_id, start_time, end_time )
);
