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
from aminopvr.epg import EpgProgram
from aminopvr.tools import printTraceback
import logging
import sys

class Schedule( object ):

    SCHEDULE_TYPE_ONCE                 = 1
    SCHEDULE_TYPE_TIMESLOT_EVERY_DAY   = 2
    SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK  = 3
    SCHEDULE_TYPE_ONCE_EVERY_DAY       = 4
    SCHEDULE_TYPE_ONCE_EVERY_WEEK      = 5
    SCHEDULE_TYPE_ANY_TIME             = 6
    SCHEDULE_TYPE_MANUAL_EVERY_DAY     = 7
    SCHEDULE_TYPE_MANUAL_EVERY_WEEKDAY = 8
    SCHEDULE_TYPE_MANUAL_EVERY_WEEKEND = 9
    SCHEDULE_TYPE_MANUAL_EVERY_WEEK    = 10

    DUPLICATION_METHOD_NONE        = 0
    DUPLICATION_METHOD_TITLE       = 1
    DUPLICATION_METHOD_SUBTITLE    = 2
    DUPLICATION_METHOD_DESCRIPTION = 4

    _id                 = -1
    _type               = -1   # manual, auto
    _channelId          = -1
    _startTime          = 0
    _endTime            = 0
    _title              = "Schedule 1"
    _preferHd           = 0
    _preferUnscrambled  = 1
    _dupMethod          = DUPLICATION_METHOD_TITLE
    _startEarly         = 0
    _endLate            = 0
    _inactive           = 0

    _logger             = logging.getLogger( 'aminopvr.Schedule' )

    def __init__( self,
                  id,       # @ReservedAssignment
                  type,     # @ReservedAssignment
                  channelId,
                  startTime,
                  endTime,
                  title,
                  preferHd,
                  preferUnscrambled,
                  dupMethod,
                  startEarly,
                  endLate,
                  inactive=0 ):
        self._id                 = id
        self._type               = type
        self._channelId          = channelId
        self._startTime          = startTime
        self._endTime            = endTime
        self._title              = title
        self._preferHd           = preferHd
        self._preferUnscrambled  = preferUnscrambled
        self._dupMethod          = dupMethod
        self._startEarly         = startEarly
        self._endLate            = endLate
        self._inactive           = inactive

    def __eq__( self, other ):
        # Not comparng _id as it might not be set at comparison time.
        # For insert/update descision it is not relevant
        if not other:
            return False
        assert isinstance( other, Schedule ), "Other object not instance of class Schedule: %r" % ( other )
        return ( self._type              == other._type              and
                 self._channelId         == other._channelId         and
                 self._startTime         == other._startTime         and
                 self._endTime           == other._endTime           and
                 self._title             == other._title             and
                 self._preferHd          == other._preferHd          and
                 self._preferUnscrambled == other._preferUnscrambled and
                 self._dupMethod         == other._dupMethod         and
                 self._startEarly        == other._startEarly        and
                 self._endLate           == other._endLate           and
                 self._inactive          == other._inactive )

    def __ne__( self, other ):
        return not self.__eq__( other )

    @property
    def id( self ):
        return self._id

    @property
    def type( self ):
        return self._type

    @type.setter
    def type( self, type ):
        self._type = type

    @property
    def channelId( self ):
        return self._channelId

    @channelId.setter
    def channelId( self, channelId ):
        self._channelId = channelId

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
        self._title = title

    @property
    def preferHd( self ):
        return self._preferHd

    @preferHd.setter
    def preferHd( self, preferHd ):
        self._preferHd = preferHd

    @property
    def preferUnscrambled( self ):
        return self._preferUnscrambled

    @preferUnscrambled.setter
    def preferUnscrambled( self, preferUnscrambled ):
        self._preferUnscrambled = preferUnscrambled

    @property
    def dupMethod( self ):
        return self._dupMethod

    @dupMethod.setter
    def dupMethod( self, dupMethod ):
        self._dupMethod = dupMethod

    @property
    def startEarly( self ):
        return self._startEarly

    @startEarly.setter
    def startEarly( self, startEarly ):
        self._startEarly = startEarly

    @property
    def endLate( self ):
        return self._endLate

    @endLate.setter
    def endLate( self, endLate ):
        self._endLate = endLate

    @property
    def inactive( self ):
        return self._inactive

    @inactive.setter
    def inactive( self, inactive ):
        self._inactive = inactive

    @classmethod
    def getAllFromDb( cls, conn, includeInactive=False ):
        schedules = []
        if conn:
            rows = []
            if includeInactive:
                rows = conn.execute( "SELECT * FROM schedules" )
            else:
                rows = conn.execute( "SELECT * FROM schedules WHERE inactive = 0" )
            for row in rows:
                schedule = cls._createScheduleFromDbDict( row )
                schedules.append( schedule )

        return schedules

    @classmethod
    def getFromDb( cls, conn, id ):
        schedule = None
        if conn:
            row = conn.execute( "SELECT * FROM schedules WHERE id = ?", ( id, ) )
            if row:
                schedule = cls._createScheduleFromDbDict( row[0] )

        return schedule

    @classmethod
    def getByTitleAndChannelIdFromDb( cls, conn, title, channelId ):
        schedule = None
        if conn:
            row = conn.execute( "SELECT * FROM schedules WHERE title = ? AND channel_id = ?", ( title, channelId ) )
            if row:
                schedule = cls._createScheduleFromDbDict( row[0] )
        return schedule

    @classmethod
    def _createScheduleFromDbDict( cls, data ):
        schedule = None
        if data:
            try:
                schedule = cls( id                = data["id"],
                                type              = data["type"],
                                channelId         = data["channel_id"],
                                startTime         = data["start_time"],
                                endTime           = data["end_time"],
                                title             = data["title"],
                                preferHd          = data["prefer_hd"],
                                preferUnscrambled = data["prefer_unscrambled"],
                                dupMethod         = data["dup_method"],
                                startEarly        = data["start_early"],
                                endLate           = data["end_late"],
                                inactive          = data["inactive"] )
            except:
                cls._logger.error( "_createScheduleFromDbDict: unexpected error: %s" % ( sys.exc_info()[0] ) )
                printTraceback()
        return schedule

    def deleteFromDB( self, conn ):
        if conn:
            conn.execute( "DELETE FROM schedules WHERE id = ?", ( self._id, ) )

    def addToDb( self, conn ):
        if conn:
#             schedule = None
#             if self._id != -1:
#                 schedule = Schedule.getFromDb( conn, self._id )
#                 if not schedule:
#                     self._id = -1

            if self._id != -1:
                conn.execute( """
                                 UPDATE
                                     schedules
                                 SET
                                     type=?,
                                     channel_id=?,
                                     start_time=?,
                                     end_time=?,
                                     title=?,
                                     prefer_hd=?,
                                     prefer_unscrambled=?,
                                     dup_method=?,
                                     start_early=?,
                                     end_late=?,
                                     inactive=? 
                                 WHERE
                                     id=%s
                              """, ( self._type,
                                     self._channel_id,
                                     self._startTime,
                                     self._endTime,
                                     self._title,
                                     self._preferHd,
                                     self._preferUnscrambled,
                                     self._dupMethod,
                                     self._startEarly,
                                     self._endLate,
                                     self._inactive,
                                     self._id ) )
            else:
                scheduleId = conn.insert( """
                                             INSERT INTO
                                                 schedules (type,
                                                            channel_id,
                                                            start_time,
                                                            end_time,
                                                            title,
                                                            prefer_hd,
                                                            prefer_unscrambled,
                                                            dup_method,
                                                            start_early,
                                                            end_late,
                                                            inactive)
                                             VALUES
                                                 (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                          """, ( self._type,
                                                 self._channelId,
                                                 self._startTime,
                                                 self._endTime,
                                                 self._title,
                                                 self._preferHd,
                                                 self._preferUnscrambled,
                                                 self._dupMethod,
                                                 self._startEarly,
                                                 self._endLate,
                                                 self._inactive ) )
                if scheduleId:
                    self._id = scheduleId

    def getPrograms( self, conn, startTime=0 ):
        programs = []
        if conn:
            epgId = None
            if self._channelId != -1:
                channel = Channel.getFromDb( conn, self._channelId )
                epgId   = channel.epgId

            if self._type == Schedule.SCHEDULE_TYPE_ONCE:
                startTime = self._startTime

            searchWhere = EpgProgram.SEARCH_TITLE

            programs = EpgProgram.getByTitleFromDb( conn, self._title, epgId, startTime, searchWhere )
        return programs

    def fromDict( self, schedule ):
        self.type              = int( schedule["type"] )
        self.channelId         = int( schedule["channel_id"] )
        self.startTime         = int( schedule["start_time"] )
        self.endTime           = int( schedule["end_time"] )
        self.title             = unicode( schedule["title"] )
        self.preferHd          = int( schedule["prefer_hd"] )
        self.preferUnscrambled = int( schedule["prefer_unscrambled"] )
        self.dupMethod         = int( schedule["dup_method"] )
        self.startEarly        = int( schedule["start_early"] )
        self.endLate           = int( schedule["end_late"] )
        self.inactive          = int( schedule["inactive"] )

    def toDict( self ):
        return { "id":                  self.id,
                 "type":                self.type,
                 "channel_id":          self.channelId,
                 "start_time":          self.startTime,
                 "end_time":            self.endTime,
                 "title":               self.title,
                 "prefer_hd":           self.preferHd,
                 "prefer_unscrambled":  self.preferUnscrambled,
                 "dup_method":          self.dupMethod,
                 "start_early":         self.startEarly,
                 "end_late":            self.endLate,
                 "inactive":            self.inactive }

    def dump( self ):
        return ( "%i: %i, %s, %i, %i-%i, %i, %i, %i, %i-%i, %i" % ( self._id, self._type, self._title, self._channelId, self._startTime, self._endTime, self._preferHd, self._preferUnscrambled, self._dupMethod, self._startEarly, self._endLate, self._inactive ) )

def main():
    sys.stderr.write( "main()\n" );

# allow this to be a module
if __name__ == '__main__':
    main()
