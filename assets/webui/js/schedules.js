/*
 *  This file is part of AminoPVR.
 *  Copyright (C) 2012  Ino Dekker
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

var _recordings = [];

var __module = "aminopvr.webui.schedules";

var _RECORDING_TYPES = [ "Single recording",
                         "Timeslot every day",
                         "Timeslot every week",
                         "Once every day",
                         "Once every week",
                         "Any time",
                         "Every day (manual)",
                         "Every weekday (manual)",
                         "Every weekend (manual)",
                         "Every week (manual)" ];

function _getScheduleListCallback( status, context, schedules )
{
    if ( status )
    {
        try
        {
            var scheduleTable = $( '#schedules tbody' );

            scheduleTable.find( 'tr' ).remove();

            _schedules = schedules;

            for ( var i in _schedules )
            {
                var schedule    = _schedules[i];

                var channel     = "Any";
                var type        = _RECORDING_TYPES[ schedule.getType() - 1 ];
                var dupMethod   = [];
                var startEarly  = "";
                var endLate     = "";

                if ( schedule.getChannelId() != -1 )
                {
                    channel = schedule.getChannelId();
                }
                if ( schedule.getDupMethod() & schedule.DUPLICATION_METHOD_TITLE )
                {
                    dupMethod.push( "Title" );
                }
                if ( schedule.getDupMethod() & schedule.DUPLICATION_METHOD_SUBTITLE )
                {
                    dupMethod.push( "Subtitle" );
                }
                if ( schedule.getDupMethod() & schedule.DUPLICATION_METHOD_DESCRIPTION )
                {
                    dupMethod.push( "Description" );
                }
                if ( dupMethod.length == 0 )
                {
                    dupMethod.push( "None" );
                }
                if ( schedule.getStartEarly() != 0 )
                {
                    startEarly = schedule.getStartEarly() + " min";
                }
                if ( schedule.getEndLate() != 0 )
                {
                    endLate = schedule.getEndLate() + " min";
                }

                var row             = $( '<tr>' ).attr( 'id', 'schedule_' + schedule.getId() );
                var titleCell       = $( '<td>' ).html( schedule.getTitle() );
                var channelCell     = $( '<td>' ).html( channel );
                var typeCell        = $( '<td>' ).html( type );
                var dupMethodCell   = $( '<td>' ).html( dupMethod.join( ', ' ) );
                var startEarlyCell  = $( '<td>' ).html( startEarly );
                var endLateCell     = $( '<td>' ).html( endLate );
                var lastRecCell     = $( '<td>' ).html( "" );
                row.append( titleCell );
                row.append( channelCell );
                row.append( typeCell );
                row.append( dupMethodCell );
                row.append( startEarlyCell );
                row.append( endLateCell );
                row.append( lastRecCell );

                scheduleTable.append( row );
            }

            logger.info( __module, "_getScheduleListCallback: Downloaded schedule list" );
        }
        catch ( e )
        {
            logger.error( __module, "_getScheduleListCallback: exception: " + e );
        }
    }

    if ( context && "callback" in context )
    {
        context["callback"]();
    }
}

$( function() {
    logger.init( true, logger.INFO );

    _schedules = [];

    aminopvr.getScheduleList( null, function( status, context, schedules ) { _getScheduleListCallback( status, context, schedules ); } );
} );
