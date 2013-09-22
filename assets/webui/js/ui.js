
var CHANNEL_COUNT               = 25;
var RECORDING_COUNT             = 25;

var devices                     = [];
var current_renderer            = -1;

var channel_offset              = 0;
var channel_list_complete       = false;
var channel_list                = new Array();
var channel_list_id             = [];
var channel_nownext_list        = new Array();
var channel_favorites_list      = [];
var fetching_channel_list       = true;


var recording_offset            = 0;
var recording_list_complete     = false;
var recording_list              = new Array();
var recording_list_div_time     = new Date( 0 );
var recording_list_div_title    = "";
var recording_list_sort         = "";
var fetching_recording_list     = true;

var channel_id                  = 0;
var recording_id                = 0;

var channel_pip_interval        = null;
var recording_pip_interval      = null;

function GetRenderer()
{
    return current_renderer;
}

function SetRenderer( id )
{
    current_renderer = id;
}

function ReloadRenderer()
{
    uiController.reloadDevice();
}

function FormatTime( time )
{
    var formatted_time = '';

    if ( time.getHours() < 10 )
    {
        formatted_time = '0';
    }
    formatted_time += time.getHours();
    formatted_time += ':';
    if ( time.getMinutes() < 10 )
    {
        formatted_time += '0';
    }
    formatted_time += time.getMinutes();

    return formatted_time;
}

function FormatDate( date )
{
    var formatted_date = '';

    if ( date.getDate() < 10 )
    {
        formatted_date = '0';
    }
    formatted_date += date.getDate();
    formatted_date += '/';
    if ( date.getMonth() < 9 )
    {
        formatted_date += '0';
    }
    formatted_date += ( date.getMonth() + 1);

    return formatted_date;
}

function FetchChannelList( edit_favorites )
{
    if ( channel_list.length == 0 )
    {
        $.mobile.showPageLoadingMsg();

        var context  = new Array();
        context["edit_favorites"] = edit_favorites;

        aminopvr.getChannelList( context, ChannelList_Fetched, true );
    }
    else
    {
        ShowChannelList();
        $.mobile.changePage( $( '#channels' ) );
    }

    FetchNowNextList();
}

function ChannelList_Fetched( status, context, channels )
{
    var edit_favorites = context["edit_favorites"];

    if ( status )
    {
        for ( var i in channels )
        {
            channel_list[channels[i].getId()] = channels[i];
            channel_list_id.push( channels[i].getId() );
        }
    
        if ( channel_favorites_list.length == 0 )
        {
            channel_favorites_list = channel_list_id;
        }
    
        if ( edit_favorites )
        {
            ShowChannelListEditFavorites();
            $.mobile.changePage( $( '#channels_favorites' ) );
        }
        else
        {
            ShowChannelList();
            $.mobile.changePage( $( '#channels' ) );
        }
    }

    $.mobile.hidePageLoadingMsg();

    fetching_channel_list = false;
}

function FetchNowNextList()
{
    var context = new Array();

    aminopvr.getNowNextProgramList( context, NowNextProgramList_Fetched, true );
}

function NowNextProgramList_Fetched( status, context, programs )
{
    console.log( 'NowNextProgramList_Fetched: get_nownext_list' );

    var refresh_list = false;
    for ( var epgId in programs )
    {
        item = programs[epgId];
        channel_nownext_list[epgId] = item;

        if ( $( '#channel_' + epgId + '_nownext' ).length )
        {
            var nownext = "";
            $.each( item, function( i, nownext_item )
            {
                var start_time  = nownext_item.getStartTime();
                var end_time    = nownext_item.getEndTime();
                var nownexttext = (i == 0) ? 'Now: ' : 'Next: ';
                nownext += '<p>' + nownexttext + FormatTime( start_time ) + ' - ' + FormatTime( end_time ) + ': ' + nownext_item.getTitle() + '</p>';
            } );

            $( '#channel_' + epgId + '_nownext' ).html( nownext );

            refresh_list = true;
        }
    }

    if ( refresh_list )
    {
        $( '#channels_list' ).listview( 'refresh' );
    }
}

function ShowChannelList()
{
    console.log( 'ShowChannelList' );

    if ( !channel_list_complete )
    {
        var items = [];

        for ( var i = 0; channel_offset + i < channel_favorites_list.length && i < CHANNEL_COUNT; i++ )
        {
            var item = channel_list[channel_favorites_list[channel_offset + i]];

            var logo = "";
            if ( item.logo != "" )
            {
                logo = '<img src="' + item.getLogo() + '">';
            }
            var nownext = '';
            var nownext = '<div id="channel_' + item.getEpgId() + '_nownext">';
            if ( channel_nownext_list[item.getEpgId()] )
            {
                $.each( channel_nownext_list[item.getEpgId()], function( i, nownext_item )
                {
                    var start_time  = nownext_item.getStartTime();
                    var end_time    = nownext_item.getEndTime();
                    var nownexttext = (i == 0) ? 'Now: ' : 'Next: ';
                    nownext += '<p>' + nownexttext + FormatTime( start_time ) + ' - ' + FormatTime( end_time ) + ': ' + nownext_item.getTitle() + '</p>';
                } );
            }
            nownext += '</div>';

//            items.push( '<li><a onclick="GoToChannel( ' + item.id + ' );">' + logo + '<h3>' + item.name + '</h3>' + nownext + '<span class="ui-li-count">' + item.id + '</span></a></li>' );
            items.push( '<li><a href="#channel-item?channel=' + item.getId() + '">' + logo + '<h3>' + item.getName() + '</h3>' + nownext + '<span class="ui-li-count">' + item.getNumber() + '</span></a></li>' );
        }

        if ( channel_offset + CHANNEL_COUNT > channel_favorites_list.length )
        {
            channel_offset = channel_favorites_list.length;
            channel_list_complete = true;
        }
        else
        {
            channel_offset += CHANNEL_COUNT;
        }

        if ( !channel_list_complete )
        {
            items.push( '<li id="channels_more">...</li>' );
        }

        // Remove more... list item.
        if ( $( '#channels_more' ) )
        {
            $( '#channels_more' ).remove();
        }

        console.log( $( '#channels_list' )[0].length );

        var test = $( '#channels_list' );

//        $( '#channels_content' ).append( $('<ul data-role="listview" id="channels_list">' + items.join( '' ) + '</ul>' ) );
//        $( '#channels_content' ).trigger( 'create' );
        if ( test[0].className == "" )
        {
            $( '#channels_list' ).append( items.join( '' ) );
            $( '#channels_list' ).trigger( 'create' );
        }
        else
        {
            $( '#channels_list' ).append( items.join( '' ) );
            $( '#channels_list' ).listview( 'refresh' );
        }
    }

    fetching_channel_list = false;
}

function ShowChannelListEditFavorites()
{
    var items = [];

    console.log( 'ShowChannelListEditFavorites' );

    if ( $( '#channels_favorites_list' )[0].className == "" )
    {
        for ( var i = 0; i < channel_list_id.length; i++ )
        {
            var item = channel_list[channel_list_id[i]];

            items.push( '<input type="checkbox" name="cb_channel_' + item.getId() + '" id="cb_channel_' + item.getId() + '" class="custom" /><label for="cb_channel_' + item.getId() + '">' + item.getNumber() + ': ' + item.getName() + '</label>' );
        }

        console.log( $( '#channels_favorites_list' )[0].length );

        $( '#channels_favorites_list' ).append( '<fieldset data-role="controlgroup"><!-- <legend>Agree to the terms:</legend> -->' + items.join( '' ) + '</fieldset>' );
        $( '#channels_favorites_list' ).trigger( 'create' );
    }

    for ( var i = 0; i < channel_favorites_list.length; i++ )
    {
        $( '#cb_channel_' + channel_favorites_list[i] ).attr( "checked", true );
    }
    $( "input[type='checkbox']" ).checkboxradio( "refresh" );
}

function ChannelsSaveFavorites()
{
    channel_favorites_list = [];

    for ( var i = 0; i < channel_list_id.length; i++ )
    {
        var item = channel_list[channel_list_id[i]];

        if ( $( '#cb_channel_' + channel_list_id[i] )[0].checked )
        {
            channel_favorites_list.push( channel_list_id[i] );
        }
    }

    console.log( $( '#channels_list' )[0].length );

    if ( channel_offset > 0 )
    {
        $( '#channels_list' ).empty();
    }

    channel_list_complete = false;
    channel_offset        = 0;

    $.cookie( 'channels_favorites', JSON.stringify( channel_favorites_list ), { 'expires' : 365 } );
    console.log( $.cookie( 'channels_favorites' ) );
}

function GoToChannel( id )
{
    if ( channel_list[id] )
    {
        var channel = channel_list[id];
        $( '#channel_title' ).html( channel.getName() );
        $( '#channel_content' ).css( 'display', 'none' );
        $( '#channel_name' ).html( '<h3>' + channel.getName() + '</h3>' );
        $( '#channel_programs_list' ).html( '' );

        channel_id = id;

        $.mobile.changePage( $( '#channel' ) );
    }
}

function ShowChannelInfo()
{
    $.mobile.showPageLoadingMsg();

    $.getJSON( 'remote.php',
    {
        ip     : current_ip,
        action : "get_epg_data",
        epg_id : channel_list[channel_id].epg_id,
        delta  : 12 * 60 * 60
    },
    function( data )
    {
        var epg_id = channel_list[channel_id].epg_id;

        $( '#channel_name' ).html( '<h3>' + channel_list[channel_id].name + '</h3>' );

        var nownext = [];
        if ( data[epg_id] && data[epg_id].length > 0 )
        {
            $.each( data[epg_id], function( i, program_item )
            {
                var start_time  = new Date( program_item.start_time * 1000 );
                var end_time    = new Date( program_item.end_time * 1000 );
                nownext.push( '<li>' + FormatTime( start_time ) + ' - ' + FormatTime( end_time ) + ': ' + program_item.title + '</li>' );
            } );
        }
        else
        {
            nownext.push( '<li>No program information available.</li>' );
        }

        $( '#channel_programs_list' ).append( nownext.join( '' ) );
        $( '#channel_programs_list' ).listview( 'refresh' );

        $.mobile.hidePageLoadingMsg();

        $( '#channel_content' ).css( 'display', 'block' );
    } )
    .error( function( jqXHR, textStatus, errorThrown )
    {
        console.log( "ShowChannelInfo: " + textStatus + ", error: " + errorThrown );
    } );
}

function ChannelPlayHere()
{
    var channel = channel_list[channel_id];

    if ( channel && $( '#channel_pip' )[0].paused )
    {
        $.mobile.showPageLoadingMsg();

        console.log( "channel: " + channel_id );

        $.getJSON( 'stream.php',
        {
            channel : channel_id,
            control : 'start'
        },
        function( data )
        {
            $( '#channel_video_status' ).html( '<p>Stream OK: ' + data + '</p>' );

            if ( data.stream_ok )
            {
                console.log( "Setting channel PIP src." );
                $( '#channel_pip' )[0].style.display = "block";
//                $( '#channel_pip' )[0].autoplay      = true;
                $( '#channel_pip' )[0].src           = 'stream.m3u8?channel=' + channel_id;

                channel_pip_interval = setInterval( function() { $( '#channel_video_status' ).html( '<p>ended: ' + $( '#channel_pip' )[0].ended + ', paused: ' + $( '#channel_pip' )[0].paused + ', networkState: ' + $( '#channel_pip' )[0].networkState + ', readyState: ' + $( '#channel_pip' )[0].readyState + '</p>' ); }, 1000 );
            }

            $.mobile.hidePageLoadingMsg();
        } )
        .error( function( jqXHR, textStatus, errorThrown )
        {
            console.log( "ChannelPlayHere: " + textStatus + ", error: " + errorThrown );
        } );
    }
}

function ChannelPlayTV()
{
    var channel = channel_list[channel_id];

    if ( channel )
    {
        console.log( "ip: " + current_ip + ", channel: " + channel_id );

        $.getJSON( 'remote.php',
        {
            ip      : current_ip,
            channel : channel_id
        },
        function( data )
        {
            console.log( "retval: " + data.retval + ", type: " + data.type );
        } )
        .error( function( jqXHR, textStatus, errorThrown )
        {
            console.log( "ChannelPlayTV: " + textStatus + ", error: " + errorThrown );
        } );
    }
}

function RecordingsToggleSort()
{
    if ( !fetching_recording_list )
    {
        fetching_recording_list = true;

        $.mobile.hidePageLoadingMsg();

        if ( recording_list_sort == "" )
        {
            recording_list_sort = "title";
        }
        else
        {
            recording_list_sort = "";
        }

        recording_list           = new Array();
        recording_offset         = 0;
        recording_list_complete  = false;
        recording_list_div_time  = new Date( 0 );
        recording_list_div_title = "";

        $( '#recordings_list' ).empty();

        FetchRecordingList();
    }
}

function FetchRecordingList()
{
    var context = new Array();

    $.mobile.showPageLoadingMsg();

    aminopvr.getRecordingList( context, RecordingList_Fetched, true, recording_offset, RECORDING_COUNT );
}

function RecordingList_Fetched( status, context, recordings )
{
    var items = [];

    if ( status )
    {
        recording_offset += recordings.length;
        if ( recordings.length != RECORDING_COUNT )
        {
            recording_list_complete = true;
        }

        for ( var i in recordings )
        {
            recording = recordings[i];
            recording_list[recording.getId()] = recording;

            var subtitle   = "";
            var logo       = "";
            var start_time = recording.getStartTime();
            if ( recording.getSubtitle() != "" )
            {
                subtitle = '<p>' + recording.getSubtitle() + '</p>';
            }

            if ( recording_list_sort == "title" )
            {
                if ( recording_list_div_title != recording.getTitle() )
                {
                    recording_list_div_title = recording.getTitle();
                    items.push( '<li data-role="list-divider">' + recording_list_div_title + '</li>' );
                }
            }
            else
            {
                if ( recording_list_div_time.getDate()  != start_time.getDate()  ||
                     recording_list_div_time.getMonth() != start_time.getMonth() ||
                     recording_list_div_time.getYear()  != start_time.getYear() )
                {
                    recording_list_div_time = start_time;
                    items.push( '<li data-role="list-divider">' + FormatDate( recording_list_div_time ) + '</li>' );
                }
            }

//            items.push( '<li><a onclick="GoToRecording( ' + item.id + ' );">' + logo + '<h3>' + item.title + '</h3>' + subtitle + '<p>Recorded on ' + FormatDate( start_time ) + ' from ' + item.channel_name + '</p></a></li>' );
            items.push( '<li><a a href="#recording-item?recording=' + recording.getId() + '"><h3>' + recording.getTitle() + '</h3>' + subtitle + '<p>Recorded on ' + FormatDate( start_time ) + ' from ' + recording.getChannelName() + '</p></a></li>' );
        }

        if ( !recording_list_complete )
        {
            items.push( '<li id="recordings_more">...</li>' );
        }

        // Remove more... list item.
        if ( $( '#recordings_more' ) )
        {
            $( '#recordings_more' ).remove();
        }

//        $( '#recordings_content' ).append( $('<ul data-role="listview" id="recordings_list">' + items.join( '' ) + '</ul>' ) );
//        $( '#recordings_content' ).trigger( 'create' );
        $( '#recordings_list' ).append( items.join( '' ) );
        if ( $( '#recordings_list' )[0].className == "" )
        {
            $( '#recordings_list' ).trigger( 'create' );

            $.mobile.changePage( $( '#recordings' ) );
        }
        else
        {
            $( '#recordings_list' ).listview( 'refresh' );
        }
    }

    $.mobile.hidePageLoadingMsg();

    fetching_recording_list = false;
}

function GoToRecording( id )
{
    if ( recording_list[id] )
    {
        var recording = recording_list[id];
        $( '#recording_title' ).html( recording.title );
        $( '#recording_content' ).css( 'display', 'none' );
        $( '#recording_name' ).html( '<h3>' + recording.title + '</h3><p>' + recording.subtitle + '</p>' );

        recording_id = id;

        $.mobile.changePage( $( '#recording' ) );
    }
}

function ShowRecordingInfo()
{
    $.mobile.showPageLoadingMsg();

    $( '#recording_name' ).html( '<h3>' + recording_list[recording_id].getTitle() + '</h3><p>' + recording_list[recording_id].getSubtitle() + '</p>' );

    $.mobile.hidePageLoadingMsg();

    $( '#recording_content' ).css( 'display', 'block' );
}

function RecordingPlayTV()
{
    var recording = recording_list[recording_id];

    if ( recording )
    {
        uiController.playRecording( recording_id );
    }
}

function UIController()
{
    this._controller = new AminoPVRController( CONTROLLER_TYPE_CONTROLLER, this );

    this.__module = function()
    {
        return "aminopvr.ui." + this.constructor.name;
    };

    this.init = function()
    {
        try
        {
            var self = this;
            window.addEventListener( "load", function()
            {
                self._onLoad();
            }, false );
        }
        catch ( e )
        {
            logger.critical( this.__module(), "init: exception: " + e );
        }
    };
    this.playRecording = function( recordingId )
    {
        message = {
            "type": "command",
            "data": {
                "command": "playRecording",
                "id":      recordingId
            }
        };
        this._controller.sendMessage( GetRenderer(), message, null, null, false );
    };
    this.reloadDevice = function()
    {
        message = {
            "type": "command",
            "data": {
                "command": "reload"
            }
        };
        this._controller.sendMessage( GetRenderer(), message, null, null, false );
    };
    this.getRendererList = function()
    {
        var context = new Array();
        context["self"] = this;
        this._controller.getListenerList( context, this.__listenerListCallback, true );
    };
    this.__listenerListCallback = function( status, context, listeners )
    {
        var renderers = [];
        if ( status )
        {
            for ( var i in listeners )
            {
                if ( listeners[i]["type"] == CONTROLLER_TYPE_RENDERER )
                {
                    renderers.push( listeners[i] );
                }
            }
        }
        context["self"]._rendererListCallback( renderers );
    };
    this._rendererListCallback = function( renderers )
    {
        $.each( renderers, function( i, item )
        {
            devices.push( item );
        } );

        if ( devices.length > 0 )
        {
            SetRenderer( devices[0].id );
        }
    };

    this._onLoad = function()
    {
        var self = this;
        window.setTimeout( function()
        {
            if ( self._controller )
            {
                self._controller.init();
            }
            self.getRendererList();
        }, 100 );
    };
    this._callback = function( data )
    {
        try
        {
            if ( data["type"] == "status" )
            {
                this._handleStatus( data["data"] );
            }
            else if ( data["type"] == "timeout" )
            {
//                    logger.debug( this.__module(), "_pollStateChange: timeout." );
            }
            else
            {
//                    logger.warning( this.__module(), "_pollStateChange: " + responseItem );
            }
            // else if ( data['type'] == 'channel' )
            // {
                // stbApi.setChannelFunction( data['channel'], 0 );
            // }
            // else if ( data['type'] == 'key' )
            // {
                // evt          = new API_KeyboardEvent;
                // evt.keyCode  = data['key'];
                // logger.info( this.__module(), "_pollStateChange: key: " + data['key'] );
                // this._keyListener( evt );
            // }
            // else if ( data['type'] == 'unknown_message' )
            // {
                // logger.warning( this.__module(), "_pollStateChange: unknown message received." );
            // }
            // else if ( data['type'] == 'timeout' )
            // {
// //                    logger.debug( this.__module(), "_pollStateChange: timeout." );
            // }
            // else
            // {
// //                    logger.warning( this.__module(), "_pollStateChange: " + responseItem );
            // }
        }
        catch ( e )
        {
            logger.error( this.__module(), "_controllerCallback: exception: " + e + ", data: " + data );
            throw e;
        }
    };

    this._handleStatus = function( data )
    {
        logger.info( this.__module(), "_handleStatus: command: " + data["status"] );
        try
        {
            {
                logger.warning( this.__module(), "_handleStatus: other command: " + data["status"] );
            }
        }
        catch ( e )
        {
            logger.error( this.__module(), "_handleStatus: exception: " + e + ", data: " + data );
            throw e;
        }
    };

}

//$.event.special.swipe.verticalDistanceThreshold = 30;

$( '#menu' ).bind( 'pagecreate', function( event )
{
} );
//$( '#channels' ).live( 'pagecreate', function( event )
//{
//    console.log( "#channels.pagecreate" );
//    channel_offset        = 0;
//    channel_list_complete = false;
//    channel_list          = [];
//    fetching_channel_list = true;
//} );
//$( '#channels' ).live( 'pageshow', function( event )
//{
//    if ( channel_offset == 0 )
//    {
//        $.mobile.showPageLoadingMsg();
//        FetchChannelList();
//    }
//} );
//$( '#channels' ).live( 'swiperight', function( event )
//{
//    $.mobile.changePage( $( '#menu' ), { reverse: true } );
//} );
//$( '#channels_favorites' ).live( 'pagebeforehide', function( event )
//{
//    ChannelsSaveFavorites();
//} );
$( '#channel' ).bind( 'pageshow', function( event )
{
//    ShowChannelInfo();
} );
$( '#channel' ).bind( 'pagehide', function( event )
{
//    StopPlayHere( 'channel' );
} );
//$( '#channel' ).live( 'swiperight', function( event )
//{
//    $.mobile.changePage( $( '#channels' ), { reverse: true } );
//} );
//$( '#recordings' ).live( 'pagecreate', function( event )
//{
//    recording_offset        = 0;
//    recording_list_complete = false;
//    recording_list          = [];
//    fetching_recording_list = true;
//} );
//$( '#recordings' ).live( 'pageshow', function( event )
//{
//    if ( recording_offset == 0 )
//    {
//        $.mobile.showPageLoadingMsg();
//        FetchRecordingList();
//    }
//} );
//$( '#recordings' ).live( 'swiperight', function( event )
//{
//    $.mobile.changePage( $( '#menu' ), { reverse: true } );
//} );
$( '#recording' ).bind( 'pageshow', function( event )
{
    ShowRecordingInfo();
} );
$( '#channel' ).bind( 'pagehide', function( event )
{
//    StopPlayHere( 'recording' );
} );
//$( '#recording' ).live( 'swiperight', function( event )
//{
//    $.mobile.changePage( $( '#recordings' ), { reverse: true } );
//} );
// $( '#devices' ).bind( 'pagecreate', function( event )
// {
    // var items = [];
// 
    // $.each( devices, function( i, item )
    // {
// //        items.push( '<li><a href="#menu" data-rel="back"><h3>' + item.ip + '</h3></a></li>' );
        // items.push( '<li><a href="#menu" data-rel="back" data-role="button" onclick="SetRenderer( \'' + item.id + '\' );">' + item.ip + '</a></li>' );
    // } );
// 
    // $( '#devices_list' ).append( items.join( '' ) );
    // if ( $( '#devices_list' )[0].className == "" )
    // {
        // $( '#devices_list' ).trigger( 'create' );
    // }
    // else
    // {
        // $( '#devices_list' ).listview( 'refresh' );
    // }
// 
    // //$( '#devices_list' ).append( items.join( '' ) );
    // //$( '#devices_content' ).trigger( 'create' );
// } );

$( document ).bind( "pagebeforechange", function( e, data )
{
    // We only want to handle changepage calls where the caller is
    // asking us to load a page by URL.
    if ( typeof data.toPage === "string" )
    {
        var u            = $.mobile.path.parseUrl( data.toPage );
        var channel_re   = /^#channel-item/;
        var recording_re = /^#recording-item/;

        console.log( "pagebeforechange: u=" + u.hash );

        if ( u.hash == "#devices" )
        {
            var items = [];

            $.each( devices, function( i, item )
            {
//        items.push( '<li><a href="#menu" data-rel="back"><h3>' + item.ip + '</h3></a></li>' );
                items.push( '<a href="#menu" data-rel="back" data-role="button" onclick="SetRenderer( \'' + item.id + '\' );">' + item.ip + '</a>' );
            } );

            $( '#devices_content' ).append( items.join( '' ) );
            if ( $( '#devices_content' )[0].className == "" )
            {
                $( '#devices_content' ).trigger( 'create' );
                $.mobile.changePage( $( '#devices' ) );

                e.preventDefault();
            }
            else
            {
                //$( '#devices_list' ).listview( 'refresh' );
                $( '#devices_content a' ).buttonMarkup();
                $( '#devices_content' ).controlgroup();
            }
        }
        else if ( u.hash == "#channels" )
        {
            if ( $.mobile.activePage && $.mobile.activePage.length > 0 && $.mobile.activePage[0].id == 'channels_favorites' )
            {
                ChannelsSaveFavorites();
            }

            FetchChannelList();

            // Make sure to tell changepage we've handled this call so it doesn't
            // have to do anything.
            e.preventDefault();
        }
        else if ( u.hash == "#channels_favorites" )
        {
            if ( channel_list.length == 0 )
            {
                $.mobile.showPageLoadingMsg();
                FetchChannelList( true );

                // Make sure to tell changepage we've handled this call so it doesn't
                // have to do anything.
                e.preventDefault();
            }
            else
            {
                ShowChannelListEditFavorites();
            }
        }
        else if ( u.hash == "#recordings" )
        {
            if ( recording_list.length == 0 )
            {
                $.mobile.showPageLoadingMsg();
                FetchRecordingList( true );

                // Make sure to tell changepage we've handled this call so it doesn't
                // have to do anything.
                e.preventDefault();
            }
        }
        else if ( u.hash.search( channel_re ) !== -1 )
        {
            var channel_id = u.hash.replace( /.*channel=/, "" );
 
            GoToChannel( channel_id );

            // Make sure to tell changepage we've handled this call so it doesn't
            // have to do anything.
            e.preventDefault();
        }
        else if ( u.hash.search( recording_re ) !== -1 )
        {
            var recording_id = u.hash.replace( /.*recording=/, "" );
 
            GoToRecording( recording_id );

            // Make sure to tell changepage we've handled this call so it doesn't
            // have to do anything.
            e.preventDefault();
        }
    }

} );
$( document ).scroll( function()
{
    var distance_to_bottom = $( document ).height() - window.innerHeight - $( document ).scrollTop();

    if ( $.mobile.activePage && $.mobile.activePage.length > 0 )
    {
        if ( $.mobile.activePage[0].id == 'channels' )
        {
            if ( !channel_list_complete && distance_to_bottom < window.innerHeight && !fetching_channel_list )
            {
                fetching_channel_list = true;
                console.log( "Fetching more channels" );
//                FetchChannelList();
                ShowChannelList();
                console.log( "Done fetching more channels" );
            }
        }
        else if ( $.mobile.activePage[0].id == 'recordings' )
        {
            if ( !recording_list_complete && distance_to_bottom < window.innerHeight && !fetching_recording_list )
            {
                fetching_recording_list = true;
                console.log( "Fetching more recordings" );
                FetchRecordingList();
                console.log( "Done fetching more recordings" );
            }
        }
    }
} );

if ( $.cookie( 'channels_favorites' ) )
{
    channel_favorites_list = JSON.parse( $.cookie( 'channels_favorites' ) );
}

//$.cookie( 'channels_favorites', '[1,2,3]', { 'expires' : 365 } );

console.log( $.cookie( 'channels_favorites' ) );

/*$.getJSON( 'remote.php',
{
    action : "discovery"
},
function( data )
{
    var items = [];

    $.each( data, function( i, item )
    {
        devices.push( item );
    } );

    if ( devices.length > 0 )
    {
        SetDeviceIP( devices[0].ip );
    }
} )
.error( function( jqXHR, textStatus, errorThrown )
{
    console.log( "FetchDevices: " + textStatus + ", error: " + errorThrown );
} );*/

logger.init();
logger.enableRemoteDebug( true );

uiController = new UIController();
uiController.init();

