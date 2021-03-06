
-- Table: epg_ids
CREATE TABLE epg_ids ( 
    epg_id   TEXT PRIMARY KEY
                  NOT NULL,
    strategy TEXT NOT NULL 
);


-- Table: schedules
CREATE TABLE schedules ( 
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
);


-- Table: genres
CREATE TABLE genres ( 
    id    INTEGER PRIMARY KEY AUTOINCREMENT
                  NOT NULL,
    genre TEXT    NOT NULL
                  UNIQUE 
);


-- Table: persons
CREATE TABLE persons ( 
    id     INTEGER PRIMARY KEY AUTOINCREMENT
                   NOT NULL,
    person TEXT    NOT NULL
                   UNIQUE 
);


-- Table: recording_program_actors
CREATE TABLE recording_program_actors ( 
    program_id INTEGER NOT NULL,
    person_id  INTEGER NOT NULL,
    PRIMARY KEY ( program_id, person_id ) 
);


-- Table: recording_program_directors
CREATE TABLE recording_program_directors ( 
    program_id INTEGER NOT NULL,
    person_id  INTEGER NOT NULL,
    PRIMARY KEY ( program_id, person_id ) 
);


-- Table: recording_program_genres
CREATE TABLE recording_program_genres ( 
    program_id INTEGER NOT NULL,
    genre_id   INTEGER NOT NULL,
    PRIMARY KEY ( program_id, genre_id ) 
);


-- Table: recording_program_presenters
CREATE TABLE recording_program_presenters ( 
    program_id INTEGER NOT NULL,
    person_id  INTEGER NOT NULL,
    PRIMARY KEY ( program_id, person_id ) 
);


-- Table: epg_program_presenters
CREATE TABLE epg_program_presenters ( 
    program_id INTEGER NOT NULL,
    person_id  INTEGER NOT NULL,
    PRIMARY KEY ( program_id, person_id ) 
);


-- Table: epg_program_genres
CREATE TABLE epg_program_genres ( 
    program_id INTEGER NOT NULL,
    genre_id   INTEGER NOT NULL,
    PRIMARY KEY ( program_id, genre_id ) 
);


-- Table: epg_program_actors
CREATE TABLE epg_program_actors ( 
    program_id INTEGER NOT NULL,
    person_id  INTEGER NOT NULL,
    PRIMARY KEY ( program_id, person_id ) 
);


-- Table: epg_programs
CREATE TABLE epg_programs ( 
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
);


-- Table: recording_programs
CREATE TABLE recording_programs ( 
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
);


-- Table: epg_program_directors
CREATE TABLE epg_program_directors ( 
    program_id INTEGER NOT NULL,
    person_id  INTEGER NOT NULL,
    PRIMARY KEY ( program_id, person_id ) 
);


-- Table: channel_urls
CREATE TABLE channel_urls ( 
    channel_id INTEGER NOT NULL,
    type       TEXT    NOT NULL,
    protocol   TEXT    NOT NULL,
    ip         TEXT    NOT NULL,
    port       INTEGER NOT NULL,
    arguments  TEXT    NOT NULL,
    scrambled  INTEGER NOT NULL,
    PRIMARY KEY ( channel_id, type ) 
);


-- Table: pending_channel_urls
CREATE TABLE pending_channel_urls ( 
    channel_id INTEGER NOT NULL,
    type       TEXT    NOT NULL,
    protocol   TEXT    NOT NULL,
    ip         TEXT    NOT NULL,
    port       INTEGER NOT NULL,
    arguments  TEXT    NOT NULL,
    scrambled  INTEGER NOT NULL,
    PRIMARY KEY ( channel_id, type ) 
);


-- Table: pending_channels
CREATE TABLE pending_channels ( 
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
);


-- Table: channels
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
                       DEFAULT '0',
    inactive   INTEGER NOT NULL
                       DEFAULT ( 0 ) 
);


-- Table: old_recordings
CREATE TABLE old_recordings ( 
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
);


-- Table: glashart_pages
CREATE TABLE glashart_pages ( 
    page    TEXT PRIMARY KEY,
    content TEXT 
);


-- Table: glashart_page_symbols
CREATE TABLE glashart_page_symbols ( 
    [key] TEXT PRIMARY KEY,
    value TEXT 
);


-- Table: recordings
CREATE TABLE recordings ( 
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
);


-- Table: db_version
CREATE TABLE db_version ( 
    db_version INTEGER 
);


-- Index: epg_programs_epg_id
CREATE INDEX epg_programs_epg_id ON epg_programs ( 
    epg_id 
);


-- Index: epg_programs_start_time
CREATE INDEX epg_programs_start_time ON epg_programs ( 
    start_time ASC 
);


-- Index: epg_programs_end_time
CREATE INDEX epg_programs_end_time ON epg_programs ( 
    end_time ASC 
);

