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

var _titleFilter = "";
var _recordings  = [];

var __module = "aminopvr.webui.recordings";

function _getRecordingListCallback( status, context, recordings )
{
    if ( status )
    {
        try
        {
            var titleSelect = $( '#title_select select[name="title_select"]' );
            titleSelect.find( "option" ).remove().end().append( '<option value="">All recordings</option>' );
            var titles = [];

            _recordings = recordings;

            for ( var i in _recordings )
            {
                var recording   = _recordings[i];

                var epgProgram  = recording.getEpgProgram();
                var title       = recording.getTitle();

                if ( epgProgram != null )
                {
                    title       = epgProgram.getTitle();
                }

                if ( titles.indexOf( title ) == -1 )
                {
                    titles.push( title );
                }
            }

            function compare( a, b )
            {
                if ( a > b )
                {
                    return -1;
                }
                else if ( a < b )
                {
                    return 1;
                }
                return 0;
            }

            titles.sort( compare );
            for ( var i in titles )
            {
                titleSelect.find( "option" ).end().append( '<option value="' + titles[i] + '">' + titles[i] + '</option>' );
            }

            titleSelect.val( _titleFilter );
            _titleFilter = titleSelect.val();

            _updateRecordingTable();

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

function _updateTitleSelection()
{
    var titleSelect = $( '#title_select select[name="title_select"]' );
    _titleFilter = titleSelect.val();

    logger.info( __module, "_updateTitleSelection: _titleFilter=" + _titleFilter );

    _updateRecordingTable();
}

function _updateRecordingTable()
{
    var recordingTable = $( '#recordings tbody' );

    recordingTable.find( 'tr' ).remove();

    for ( var i in _recordings )
    {
        var recording   = _recordings[i];

        var epgProgram  = recording.getEpgProgram();
        var title       = recording.getTitle();
        var subtitle    = "";
        var description = "";
        var channel     = recording.getChannelName();
        var length      = Math.round( recording.getLength() / 60 ) + " mins";
        var fileSize    = Math.round( recording.getFileSize() ) + " MB";

        if ( epgProgram != null )
        {
            title       = epgProgram.getTitle();
            subtitle    = epgProgram.getSubtitle();
            description = epgProgram.getDescription();
        }
        if ( recording.getChannel() != null)
        {
            channel     = recording.getChannel().getName();
        }

        if ( _titleFilter == "" || title == _titleFilter )
        {
            var optionRemove    = $( '<a>' ).attr( 'href', '#' ).html( 'Remove' ).click( function() {
                var recordingId = $(this).parents( 'tr' ).attr( 'id' );
                logger.warning( __module, "recordingId=" + recordingId );
                RemoveRecording( recordingId, false );
            } );
            var optionRerecord  = $( '<a>' ).attr( 'href', '#' ).html( 'Remove & Re-record' ).click( function() {
                var recordingId = $(this).parents( 'tr' ).attr( 'id' );
                logger.warning( __module, "recordingId=" + recordingId );
                RemoveRecording( recordingId, true );
            } );
            var row             = $( '<tr>' ).attr( 'id', 'recording_' + recording.getId() );
            var titleCell       = $( '<td>' ).html( title );
            var subtitleCell    = $( '<td>' ).html( subtitle );
            var timeCell        = $( '<td>' ).html( recording.getStartTime()._toHuman() );
            var channelCell     = $( '<td>' ).html( channel );
            var lengthCell      = $( '<td>' ).html( length );
            var fileSizeCell    = $( '<td>' ).html( fileSize );
            var optionsCell     = $( '<td>' ).attr( 'rowspan', 2 ).append( optionRemove ).append( $( '<br>' ) ).append( optionRerecord );
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
    }
}

function RemoveRecording( recordingId, rerecord )
{
    rerecord    = rerecord || false;
    recordingId = recordingId.replace( 'recording_', '' );

    for ( var i in _recordings )
    {
        var recording = _recordings[i];
        if ( recording.getId() == recordingId )
        {
            if ( recording.deleteFromDb( rerecord ) )
            {
                aminopvr.getRecordingList( null, function( status, context, recordings ) { _getRecordingListCallback( status, context, recordings ); } );
            }
        }
    }
}

$( function() {
    logger.init( true, logger.INFO );

    _recordings = [];

    var titleSelect = $( '#title_select select[name="title_select"]' );
    titleSelect.change( function( event ) { _updateTitleSelection(); } );

    aminopvr.getRecordingList( null, function( status, context, recordings ) { _getRecordingListCallback( status, context, recordings ); } );
} );
