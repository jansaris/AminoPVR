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
from aminopvr.database.cache import Cache
from aminopvr.database.channel import Channel, ChannelAbstract
from aminopvr.database.epg import EpgProgram
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

    _logger             = logging.getLogger( 'aminopvr.Schedule' )

    def __init__( self, id=-1 ):    # @ReservedAssignment
        self._id                = int( id )
        self._type              = Schedule.SCHEDULE_TYPE_ONCE
        self._channelId         = -1
        self._startTime         = 0
        self._endTime           = 0
        self._title             = "Title"
        self._preferHd          = False
        self._preferUnscrambled = False
        self._dupMethod         = Schedule.DUPLICATION_METHOD_TITLE
        self._startEarly        = 0
        self._endLate           = 0
        self._inactive          = False
        self._channel           = None

    def __eq__( self, other ):
        # Not comparing _id as it might not be set at comparison time.
        # For insert/update decision it is not relevant
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
    def type( self, type ): # @ReservedAssignment
        self._type = int( type )

    @property
    def channelId( self ):
        return self._channelId

    @channelId.setter
    def channelId( self, channelId ):
        self._channelId = int( channelId )

    @property
    def channel( self ):
        return self._channel
    
    @channel.setter
    def channel( self, channel ):
        self._channel = channel
        if channel:
            if not isinstance( channel, ChannelAbstract ):
                assert False, "Schedule.channel: channel not a ChannelAbstract instance: %r" % ( channel )
                self._channel   = None
                self._channelId = -1;
            else:
                self._channelId = channel.id

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
    def preferHd( self ):
        return self._preferHd

    @preferHd.setter
    def preferHd( self, preferHd ):
        self._preferHd = int( preferHd )

    @property
    def preferUnscrambled( self ):
        return self._preferUnscrambled

    @preferUnscrambled.setter
    def preferUnscrambled( self, preferUnscrambled ):
        self._preferUnscrambled = int( preferUnscrambled )

    @property
    def dupMethod( self ):
        return self._dupMethod

    @dupMethod.setter
    def dupMethod( self, dupMethod ):
        self._dupMethod = int( dupMethod )

    @property
    def startEarly( self ):
        return self._startEarly

    @startEarly.setter
    def startEarly( self, startEarly ):
        self._startEarly = int( startEarly )

    @property
    def endLate( self ):
        return self._endLate

    @endLate.setter
    def endLate( self, endLate ):
        self._endLate = int( endLate )

    @property
    def inactive( self ):
        return self._inactive

    @inactive.setter
    def inactive( self, inactive ):
        self._inactive = int( inactive )

    @classmethod
    def getAllFromDb( cls, conn ):
        schedules = []
        if conn:
            rows = conn.execute( "SELECT * FROM schedules" )
            for row in rows:
                schedule = cls._createScheduleFromDbDict( conn, row )
                schedules.append( schedule )

        return schedules

    @classmethod
    def getFromDb( cls, conn, id ):  # @ReservedAssignment
        schedule = Cache().get( "schedules", id )
        if not schedule and conn:
            row = conn.execute( "SELECT * FROM schedules WHERE id = ?", ( id, ) )
            if row:
                schedule = cls._createScheduleFromDbDict( conn, row[0] )

        return schedule

    @classmethod
    # TODO: this is odd, should title/channel_id combi be unique?
    def getByTitleAndChannelIdFromDb( cls, conn, title, channelId ):
        schedule = None
        if conn:
            row = conn.execute( "SELECT * FROM schedules WHERE title = ? AND channel_id = ?", ( title, channelId ) )
            if row:
                schedule = cls._createScheduleFromDbDict( conn, row[0] )
        return schedule

    @classmethod
    def search( cls, conn, query, shortForm=True ):
        schedules   = []
        query       = '%' + query + '%'
        if conn:
            rows   = None
            select = "*"
            if shortForm:
                select = "DISTINCT title"
            rows = conn.execute( "SELECT %s FROM schedules WHERE title LIKE ?" % ( select ), ( query, ) )
            if shortForm:
                schedules = [ row["title"] for row in rows ]
            else:
                schedules = [ cls._createScheduleFromDbDict( conn, row ) for row in rows ]
        return schedules

    @classmethod
    def _createScheduleFromDbDict( cls, conn, data ):
        schedule = None
        if data:
            try:
                schedule                    = cls( data["id"] )
                schedule.type               = data["type"]
                schedule.channelId          = data["channel_id"]
                schedule.startTime          = data["start_time"]
                schedule.endTime            = data["end_time"]
                schedule.title              = data["title"]
                schedule.preferHd           = data["prefer_hd"]
                schedule.preferUnscrambled  = data["prefer_unscrambled"]
                schedule.dupMethod          = data["dup_method"]
                schedule.startEarly         = data["start_early"]
                schedule.endLate            = data["end_late"]
                schedule.inactive           = data["inactive"]

                if schedule.channelId != -1:
                    schedule.channel = Channel.getFromDb( conn, schedule.channelId )
                    if not schedule.channel:
                        schedule.channelId = -1

                Cache().cache( "schedules", schedule.id, schedule )

            except:
                cls._logger.error( "_createScheduleFromDbDict: unexpected error: %s" % ( sys.exc_info()[0] ) )
                printTraceback()
        return schedule

    def deleteFromDb( self, conn ):
        if conn:
            conn.execute( "DELETE FROM schedules WHERE id = ?", ( self._id, ) )

            Cache().purge( "schedules", self._id )

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
                                     id=?
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

            Cache().cache( "schedules", self.id, self )

    def getPrograms( self, conn, startTime=0 ):
        programs = []
        if conn:
            epgId = None
            if self._channelId != -1:
                channel = Channel.getFromDb( conn, self._channelId )
                epgId   = channel.epgId

#            if self._type == Schedule.SCHEDULE_TYPE_ONCE:
#                startTime = None #self._startTime

            searchWhere = EpgProgram.SEARCH_TITLE

            programs = EpgProgram.getByTitleFromDb( conn, self._title, epgId, startTime, searchWhere )
        return programs

    @classmethod
    def fromDict( cls, data, id=-1 ):  # @ReservedAssignment
        schedule = None
        if data:
            try:
                schedule                    = cls( id )
                schedule.type               = data["type"]
                schedule.channelId          = data["channel_id"]
                schedule.startTime          = data["start_time"]
                schedule.endTime            = data["end_time"]
                schedule.title              = data["title"]
                schedule.preferHd           = data["prefer_hd"]
                schedule.preferUnscrambled  = data["prefer_unscrambled"]
                schedule.dupMethod          = data["dup_method"]
                schedule.startEarly         = data["start_early"]
                schedule.endLate            = data["end_late"]
                schedule.inactive           = data["inactive"]
            except:
                cls._logger.error( "fromDict: unexpected error: %s" % ( sys.exc_info()[0] ) )
                printTraceback()
        return schedule

    def toDict( self ):
        scheduleDict = { "id":                  self.id,
                         "type":                self.type,
                         "start_time":          self.startTime,
                         "end_time":            self.endTime,
                         "title":               self.title,
                         "prefer_hd":           self.preferHd,
                         "prefer_unscrambled":  self.preferUnscrambled,
                         "dup_method":          self.dupMethod,
                         "start_early":         self.startEarly,
                         "end_late":            self.endLate,
                         "inactive":            self.inactive }

        if self.channel:
            scheduleDict["channel_id"]  = self.channelId
            scheduleDict["channel"]     = self.channel.toDict()
        else:
            scheduleDict["channel_id"]  = -1

        return scheduleDict

    def dump( self ):
        return ( "%i: %i, %s, %i, %i-%i, %i, %i, %i, %i-%i, %i" % ( self._id, self._type, self._title, self._channelId, self._startTime, self._endTime, self._preferHd, self._preferUnscrambled, self._dupMethod, self._startEarly, self._endLate, self._inactive ) )

def main():
    sys.stderr.write( "main()\n" )

# allow this to be a module
if __name__ == '__main__':
    main()
