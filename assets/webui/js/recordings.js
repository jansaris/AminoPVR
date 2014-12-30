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

var __module = "aminopvr.webui.recordings";

function _getRecordingListCallback( status, context, recordings )
{
    if ( status )
    {
        try
        {
            var recordingTable = $( '#recordings tbody' );

            recordingTable.find( 'tr' ).remove();

            _recordings = recordings;

            for ( var i in _recordings )
            {
                var recording   = _recordings[i];

                var epgProgram  = recording.getEpgProgram();
                var title       = recording.getTitle();
                var subtitle    = "";
                var description = "";
                var length      = Math.round( recording.getLength() / 60 ) + " mins";
                var fileSize    = Math.round( recording.getFileSize() / 1024 / 1024 ) + " MB";

                if ( epgProgram != null )
                {
                    title       = epgProgram.getTitle();
                    subtitle    = epgProgram.getSubtitle();
                    description = epgProgram.getDescription();
                }

                var row             = $( '<tr>' ).attr( 'id', 'recording_' + recording.getId() );
                var titleCell       = $( '<td>' ).html( title );
                var subtitleCell    = $( '<td>' ).html( subtitle );
                var timeCell        = $( '<td>' ).html( recording.getStartTime()._toHuman() );
                var channelCell     = $( '<td>' ).html( recording.getChannelName() );
                var lengthCell      = $( '<td>' ).html( length );
                var fileSizeCell    = $( '<td>' ).html( fileSize );
                var optionsCell     = $( '<td>' ).html( "" );
                row.append( titleCell );
                row.append( subtitleCell );
                row.append( timeCell );
                row.append( channelCell );
                row.append( lengthCell );
                row.append( fileSizeCell );
                row.append( optionsCell );

                recordingTable.append( row );

                var row             = $( '<tr>' );
                var descriptionCell = $( '<td>' ).attr( 'colspan', 3 ).html( description );
                row.append( descriptionCell );

                recordingTable.append( row );
            }

            logger.info( __module, "_getRecordingListCallback: Downloaded recording list" );
        }
        catch ( e )
        {
            logger.error( __module, "_getRecordingListCallback: exception: " + e );
        }
    }

    if ( context && "callback" in context )
    {
        context["callback"]();
    }
}

$( function() {
    logger.init( true, logger.INFO );

    _recordings = [];

    aminopvr.getRecordingList( null, function( status, context, recordings ) { _getRecordingListCallback( status, context, recordings ); } );
} );
