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

var _scheduledRecordings = [];

var __module = "aminopvr.webui.status";

function _getScheduledRecordingListCallback( status, context, recordings )
{
    if ( status )
    {
        try
        {
            var scheduledRecordingTable = $( '#scheduled_recordings tbody' );

            scheduledRecordingTable.find( 'tr' ).remove();

            _scheduledRecordings = recordings;

            for ( var i in _scheduledRecordings )
            {
                var recording   = _scheduledRecordings[i];
                var row         = $( '<tr>' );
                var timeCell    = $( '<td>' ).html( recording.getStartTime()._toHuman() );
                var programCell = $( '<td>' );
                var title       = recording.getTitle();
                if ( recording.getEpgProgram() )
                {
                    var epgProgram = recording.getEpgProgram();
                    title          = epgProgram.getTitle();
                    if ( epgProgram.getSubtitle() )
                    {
                        title += ": " + epgProgram.getSubtitle();
                    }
                }
                programCell.html( title );
                var channelCell = $( '<td>' ).html( recording.getChannelName() );
                row.append( timeCell );
                row.append( programCell );
                row.append( channelCell );

                scheduledRecordingTable.append( row );
            }

            logger.info( __module, "_getScheduledRecordingListCallback: Downloaded scheduled recording list" );
        }
        catch ( e )
        {
            logger.error( __module, "_getScheduledRecordingListCallback: exception: " + e );
        }
    }
}

function _getStorageInfoCallback( status, context, storageInfo )
{
    if ( status )
    {
        var usedSpace = storageInfo["total_size"] - storageInfo["available_size"];
        $( '#disk_usage_total' ).html( storageInfo["total_size"] + " MB" );
        $( '#disk_usage_used' ).html( usedSpace + " MB" );
        $( '#disk_usage_free' ).html( storageInfo["available_size"] + " MB" );
    }
}

function _getEpgInfoCallback( status, context, epgInfo )
{
    if ( status )
    {
        $( '#program_data_provider' ).html( epgInfo["provider"] );
        $( '#program_data_last_update' ).html( new Date( epgInfo["last_update"] * 1000 )._toHuman() );
        $( '#program_data_num_programs' ).html( epgInfo["num_programs"] );
        $( '#program_data_info_till' ).html( new Date( epgInfo["last_program"] * 1000 )._toHuman() );
    }
}

$( function() {
    logger.init( true, logger.INFO );

    _scheduledRecordings = [];

    aminopvr.getScheduledRecordingList( null, function( status, context, recordings ) { _getScheduledRecordingListCallback( status, context, recordings ); } );
    aminopvr.getStorageInfo( null, function( status, context, storageInfo ) { _getStorageInfoCallback( status, context, storageInfo ); } );
    aminopvr.getEpgInfo( null, function( status, context, epgInfo ) { _getEpgInfoCallback( status, context, epgInfo ); } );
} );
