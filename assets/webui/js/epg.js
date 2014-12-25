var _currentProgramDetails       = null;
var _currentEpgProgram           = null;
var _currentSchedule             = null;
var _scheduleMatchRequestBusy    = false;
var _programs       = {};
var _channels       = {};
var _schedules      = {};
var _epgData        = {};
var _epgDataValid   = false;
var _startTime      = 0;
var _endTime        = 0;
var _spinner        = null;

var _TIMEBLOCKS             = 12;
var _TIMEBLOCK_LENGTH       = 5;
var _COLS_PER_BLOCK         = 3;
var _PERCENTAGE_PER_BLOCK   = 95.0 / (_TIMEBLOCKS * _COLS_PER_BLOCK);

var __module = "aminopvr.webui.epg";

function Init()
{
    logger.init( true );

    _channels       = {};
    _programs       = {};
    _epgData        = {};
    _epgDataValid   = false;

    var now     = Math.round( new Date().getTime() / 1000 );
    _startTime  = roundTo15Minutes( now );
    _endTime    = _startTime + (_TIMEBLOCK_LENGTH * _COLS_PER_BLOCK * 60 * _TIMEBLOCKS);

    var channelRequestContext = {};
    channelRequestContext["callback"] = function () { _populateChannelsInEpgGrid(); }; 

    var programRequestContext = {};
    programRequestContext["callback"] = function () { _populateProgramsInEpgGrid(); }; 

    var timeblockSelect = $( '#timeblock_select input[name="timeblock_select"]' );
    timeblockSelect.attr( 'step', 60 * _TIMEBLOCK_LENGTH * _COLS_PER_BLOCK );
    timeblockSelect.change( function( event ) { _updateTimeblock(); } );

    _showLoadingIcon();
    _initEpgGrid();

    aminopvr.getChannelList( channelRequestContext, function( status, context, channels ) { _getChannelListCallback( status, context, channels ); } );
    aminopvr.getProgramList( null, _startTime, _endTime, programRequestContext, function( status, context, programs ) { _getProgramListCallback( status, context, programs ); } );
    aminopvr.getScheduleList( null, function( status, context, schedules ) { _getScheduleListCallback( status, context, schedules ); } );
}

function _showLoadingIcon( container )
{
    container = container || $( 'body' );
    if ( _spinner == null )
    {
        if ( container.is( $( 'body' ) ) )
        {
            $( '#screen' ).css( {
                'opacity':  0.3,
                'width':    $(document).width(),
                'height':   $(document).height(),
                'display':  'block'
            } );
        }

        _spinner = new Spinner().spin();
        container.append( _spinner.el );
    }
}

function _hideLoadingIcon()
{
    if ( _spinner != null )
    {
        _spinner.stop();
        _spinner = null;

        $( '#screen' ).css( 'display', 'none' );
    }
}

function _getProgramListCallback( status, context, programs )
{
    if ( status )
    {
        try
        {
            _epgData        = programs;
            _epgDataValid   = true;
            for ( var epgId in programs )
            {
                for ( var i in programs[epgId] )
                {
                    if ( !(programs[epgId][i].getId() in _programs) )
                    {
                        _programs[programs[epgId][i].getId()] = programs[epgId][i];
                    }
                }
            }

            logger.info( __module, "_getProgramListCallback: Downloaded epg program list" );
        }
        catch ( e )
        {
            logger.error( __module, "_getProgramListCallback: exception: " + e );
        }
    }

    if ( context && "callback" in context )
    {
        context["callback"]();
    }
}

function _getChannelListCallback( status, context, channels )
{
    if ( status )
    {
        try
        {
            _channels = {};
            for ( var i in channels )
            {
                if ( !(channels[i].getId() in _channels) )
                {
                    _channels[channels[i].getId()] = channels[i];
                }
            }

            logger.info( __module, "_getChannelListCallback: Downloaded channel list" );
        }
        catch ( e )
        {
            logger.error( __module, "_getChannelListCallback: exception: " + e );
        }
    }

    if ( context && "callback" in context )
    {
        context["callback"]();
    }
}

function _getScheduleListCallback( status, context, schedules )
{
    if ( status )
    {
        try
        {
            _schedules = {};
            for ( var i in schedules )
            {
                if ( !(schedules[i].getId() in _schedules) )
                {
                    _schedules[schedules[i].getId()] = schedules[i];
                }
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

function _initEpgGrid()
{
    var epgGridHeader = $( '#program_grid > thead' );
    var headerRow     = epgGridHeader.find( '#program_grid_header' );

    if ( !headerRow.length )
    {
        headerRow = $( '<tr>' );
        headerRow.attr( 'id', 'program_grid_header' );
        headerRow.addClass( 'menu' );

        var leftCell = $( '<th>' );
        leftCell.attr( 'align', 'right' );
        leftCell.addClass( 'scroll_time' );
        leftCell.click( function() { ShowEarlierTimeblock(); } );
        leftCell.html( "&lt;" );
        headerRow.append( leftCell );

        var percentage = _COLS_PER_BLOCK * _PERCENTAGE_PER_BLOCK;
        for ( var i = 0; i < _TIMEBLOCKS; i++ )
        {
            var headerCell = $( '<th>' );
            headerCell.attr( 'colspan', _COLS_PER_BLOCK );
            headerCell.attr( 'align', 'center' );
            headerCell.addClass( 'nowrap' );
            headerCell.css( 'width', percentage.toFixed( 1 ) + '%' );
            headerRow.append( headerCell );
        }

        var rightCell = $( '<th>' );
        rightCell.attr( 'align', 'left' );
        rightCell.addClass( 'scroll_time' );
        rightCell.click( function() { ShowLaterTimeblock(); } );
        rightCell.html( "&gt;" );
        headerRow.append( rightCell );

        epgGridHeader.prepend( headerRow );
    }

    _updateEpgGridHeader();
}

function _updateEpgGridHeader()
{
    var epgGridHeader = $( '#program_grid > thead' );
    var headerRow     = epgGridHeader.find( '#program_grid_header' );
    var headerCells   = headerRow.find( 'th' ).slice( 1, -1 ).each( function ( index ) {
        $(this).html( new Date( (_startTime + (index * 15 * 60)) * 1000 )._toHHMM() );
    } );
    $( '#timeblock' ).html( new Date( _startTime * 1000 )._toHuman() );

    var timeblockSelect = $( '#timeblock_select input[name="timeblock_select"]' );
    timeblockSelect.val( new Date( _startTime * 1000 )._toLocalJSON() );
}

function _populateChannelsInEpgGrid()
{
    var epgGrid = $( '#program_grid' );

    var channels = new Array();
    for ( var i in _channels )
    {
        channels.push( _channels[i] );
    }

    function compare( a, b )
    {
        if ( a.getNumber() < b.getNumber() )
        {
            return -1;
        }
        if ( a.getNumber() > b.getNumber() )
        {
            return 1;
        }
        return 0;
    }

    channels.sort( compare );

    for ( var i in channels )
    {
        var channel     = channels[i];
        var channelIcon = '<img src="' + channel.getLogo() + '" title="' + channel.getNumber() + ' - ' + channel.getName() + '"><br/>' + channel.getNumber();
        var channelCell = $( '<td></td>' ).addClass( "channel" ).append( channelIcon );
        var channelRow  = $( '<tr></tr>' ).attr( 'id', 'channel_' + channel.getId() ).append( channelCell );
        epgGrid.append( channelRow );
    }

    if ( _epgDataValid )
    {
        _populateProgramsInEpgGrid();
    }
}

function _populateProgramsInEpgGrid()
{
    var epgGrid = $( '#program_grid' );

    for ( var i in _channels )
    {
        var channel    = _channels[i];
        var channelRow = $( '#channel_' + channel.getId() );

        channelRow.find( 'td:not( .channel )' ).remove();

        if ( channel.getEpgId() in _epgData )
        {
            var blockOffset = 0
            var programs    = _epgData[channel.getEpgId()];

            function compare( a, b )
            {
                if ( a.getStartTime().getTime() < b.getStartTime().getTime() )
                {
                    return -1;
                }
                if ( a.getStartTime().getTime() > b.getStartTime().getTime() )
                {
                    return 1;
                }
                return 0;
            }

            programs.sort( compare );

            for ( var j in programs )
            {
                var program             = programs[j];
                var programStartTime    = program.getStartTime().getTime() / 1000;
                var programEndTime      = program.getEndTime().getTime() / 1000;
                if ( (programEndTime > _startTime) && (programStartTime < _endTime) )
                {
                    if ( programStartTime < _startTime )
                    {
                        programStartTime = _startTime;
                    }
                    if ( programEndTime > _endTime )
                    {
                        programEndTime = _endTime;
                    }

                    var startBlock = _calculateBlockOffset( programStartTime - _startTime );
                    var endBlock   = _calculateBlockOffset( programEndTime - _startTime );

                    if ( startBlock > blockOffset )
                    {
                        var blocks      = startBlock - blockOffset;
                        var percentage  = blocks * _PERCENTAGE_PER_BLOCK;
                        var programCell = $( '<td></td>' );
                        programCell.attr( 'colspan', blocks );
                        programCell.css( 'width', percentage.toFixed( 1 ) + '%' );
                        programCell.addClass( "small program truncate" );
                        programCell.html( "..." );
                        channelRow.append( programCell );
                    }
                    if ( endBlock > blockOffset )
                    {
                        var blocks      = endBlock - startBlock;
                        var percentage  = blocks * _PERCENTAGE_PER_BLOCK;
                        var programCell = $( '<td></td>' );
                        programCell.attr( 'id', 'program_' + program.getId() );
                        programCell.attr( 'colspan', blocks );
                        programCell.css( 'width', percentage.toFixed( 1 ) + '%' );
                        programCell.addClass( "small program truncate" );
                        if ( program.getGenres().length > 0 )
                        {
                            programCell.addClass( "cat_" + program.getGenres()[0] );
                        }

                        var div = $( '<div>' );
                        var span = $( '<span>' );
                        if ( program.getSubtitle() != "" )
                        {
                            span.html( program.getTitle() + ":<br />" + program.getSubtitle() );
                        }
                        else
                        {
                            span.html( program.getTitle() );
                        }
                        div.append( span );
                        programCell.append( div );
                        channelRow.append( programCell );

                        programCell.click( function() {
                            var programId = $(this).attr( 'id' );
                            ShowProgramDetails( programId );
                        } );

                        blockOffset = endBlock;
                    }
                }
            }
        }
    }

    _hideLoadingIcon();
}

function _calculateBlockOffset( timestamp )
{
    offset = timestamp / (_TIMEBLOCK_LENGTH * 60.0)
    return Math.round( offset )
}

function ShowEarlierTimeblock()
{
    var timespan = _endTime - _startTime;
    _startTime   = _startTime - timespan;
    _endTime     = _endTime - timespan;

    _updateEpgGrid();
}

function ShowLaterTimeblock()
{
    var timespan = _endTime - _startTime;
    _startTime   = _startTime + timespan;
    _endTime     = _endTime + timespan;

    _updateEpgGrid();
}

function _updateTimeblock()
{
    var timespan = _endTime - _startTime;
    _startTime   = Math.round( new Date( $( '#timeblock_select input[name="timeblock_select"]' ).val() )._getUTCTime() / 1000 );
    _startTime   = roundTo15Minutes( _startTime );
    _endTime     = _startTime + timespan;

    _updateEpgGrid();
}

function _updateEpgGrid()
{
    _showLoadingIcon();

    _epgDataValid = false;

    _hideProgramDetails();
    _updateEpgGridHeader();

    var programRequestContext = {};
    programRequestContext["callback"] = function () { _populateProgramsInEpgGrid(); }; 
    aminopvr.getProgramList( null, _startTime, _endTime, programRequestContext, function( status, context, programs ) { _getProgramListCallback( status, context, programs ); } );
}

function ShowProgramDetails( program )
{
    if ( _currentProgramDetails != program )
    {
        _hideProgramDetails();

        var programDetails = $( "#program_details_proto" ).clone();
        programDetails.attr( "id", "program_details" );
        programDetails.find( ".program_details_body" ).attr( 'colspan', _COLS_PER_BLOCK * _TIMEBLOCKS );

        var programId  = program.replace( 'program_', '' );
        if ( !(programId in _programs) )
        {
            aminopvr.getEpgProgramById( programId, null, function( status, context, epgProgram ) { _programDetailsCallback( status, context, epgProgram ); }, true );
        }
        else
        {
            _currentEpgProgram = _programs[programId];
            aminopvr.getEpgProgramsByTitleAndEpgId( _currentEpgProgram.getTitle(), null, null, function( status, context, programs ) { _programDetailsSimilarProgramsCallback( status, context, programs ); }, true );
        }

        $( "#" + program ).closest( "tr" ).after( programDetails );
        $( "#" + program ).addClass( "selectedProgram" );

        if ( programId in _programs )
        {
            $( "#program_details .program_details_title" ).html( _programs[programId].getTitle() );
            if ( _programs[programId].getSubtitle() != null )
            {
                $( "#program_details .program_details_subtitle" ).html( _programs[programId].getSubtitle() );
            }
        }

        ProgramDetails();

        _currentProgramDetails = program;

        window.location.hash = program;
    }
}

function _hideProgramDetails()
{
    if ( _currentProgramDetails != null )
    {
        var programCell = $( "#" + _currentProgramDetails );
        if ( programCell != null )
        {
            programCell.removeClass( "selectedProgram" );
        }
        _currentProgramDetails = null;
        _currentEpgProgram     = null;
        _currentSchedule       = null;
    }

    $( "#program_details" ).remove();
}

function _programDetailsCallback( status, context, epgProgram )
{
    if ( status )
    {
        try
        {
            if ( epgProgram != null )
            {
                $( "#program_details .program_details_details" ).html( epgProgram.getDescription() );

                _currentEpgProgram = epgProgram;
                aminopvr.getEpgProgramsByTitleAndEpgId( _currentEpgProgram.getTitle(), null, null, function( status, context, programs ) { _programDetailsSimilarProgramsCallback( status, context, programs ); }, true );
            }

            logger.info( __module, "_programDetailsCallback: Downloaded epg program" );
        }
        catch ( e )
        {
            logger.error( __module, "_programDetailsCallback: exception: " + e );
        }
    }
};

function _programDetailsSimilarProgramsCallback( status, context, similarPrograms )
{
    if ( status )
    {
        try
        {
            var similarProgramList = "Similar programs: ";
            for ( var epgId in similarPrograms )
            {
                for ( var i in similarPrograms[epgId] )
                {
                    similarProgramList += similarPrograms[epgId][i].getTitle() + ", ";
                }
            }

            $( "#program_details .program_details_similar" )[0].innerHTML = similarProgramList;

            logger.info( __module, "_programDetailsSimilarProgramsCallback: Downloaded epg program list" );
        }
        catch ( e )
        {
            logger.error( __module, "_programDetailsSimilarProgramsCallback: exception: " + e );
        }
    }
}

function ProgramDetails()
{
    $( ".program_details_record" ).css( "display", "none" );
    $( ".program_details_section" ).css( "display", "block" );
}

function ProgramDetailsRecord()
{
    var recordSchedules     = $( '#program_details select[name="record_schedules"]' );
    var recordChannel       = $( '#program_details select[name="record_channel"]' );
    var recordType          = $( '#program_details select[name="record_type"]' );
    var recordStartTime     = $( '#program_details input[name="record_starttime"]' );
    var recordEndTime       = $( '#program_details input[name="record_endtime"]' );
    var recordTitle         = $( '#program_details input[name="record_title"]' );
    var recordDupMethod     = $( '#program_details select[name="record_duplicate_method"]' );
    var recordStartEarly    = $( '#program_details input[name="record_start_early"]' );
    var recordEndLate       = $( '#program_details input[name="record_end_late"]' );
    var recordInactive      = $( '#program_details input[name="record_inactive"]' );
    var recordRecord        = $( '#program_details input[name="record_record"]' );
    var recordRemove        = $( '#program_details input[name="record_remove"]' );
    if ( _currentEpgProgram != null )
    {
        recordSchedules.find( "option" ).remove().end().append( '<option value="-1">New...</option>' ).val( '-1' );
        for ( var i in _schedules )
        {
            if ( _schedules[i].getTitle() == _currentEpgProgram.getTitle() )
            {
                recordSchedules.append( $( "<option></option>" ).attr( "value", i ).text( _schedules[i].getTitle() ) ).val( i ); 
            }
        }

        var channels = new Array();
        for ( var i in _channels )
        {
            channels.push( _channels[i] );
        }

        function compare( a, b )
        {
            if ( a.getNumber() < b.getNumber() )
            {
                return -1;
            }
            if ( a.getNumber() > b.getNumber() )
            {
                return 1;
            }
            return 0;
        }

        channels.sort( compare );

        recordChannel.find( "option" ).remove().end().append( '<option value="-1">Any channel</option>' ).val( '-1' );
        for ( var i in channels )
        {
            recordChannel.append( $( "<option></option>" ).attr( "value", channels[i].getId() ).text( channels[i].getName() ) ); 
        }

        recordSchedules.change( function( event ) { _updateRecordingSchedulesSelection(); } );

        _updateRecordingSchedulesSelection();
    }

    recordStartTime.attr( 'step', 60 );
    recordEndTime.attr( 'step', 60 );

    recordChannel.unbind( "change" );
    recordType.unbind( "change" );
    recordTitle.unbind( "input" );
    recordDupMethod.unbind( "change" );
    recordStartTime.unbind( "input" );
    recordEndTime.unbind( "input" );
    recordInactive.unbind( "change" );
    recordStartEarly.unbind( "input" );
    recordEndLate.unbind( "input" );
    recordStartEarly.unbind( "keyup" );
    recordEndLate.unbind( "keyup" );

    recordChannel.change( function( event ) { _updateRecordingMatches(); } );
    recordType.change( function( event ) { _updateRecordingMatches(); } );
    recordTitle.on( "input", function( event ) { _updateRecordingMatches(); } );
    recordDupMethod.change( function( event ) { _updateRecordingMatches(); } );
    recordStartTime.on( "input", function( event ) { _updateRecordingMatches(); } );
    recordEndTime.on( "input", function( event ) { _updateRecordingMatches(); } );
    recordInactive.change( function( event ) { _updateRecordingMatches(); } );

    recordStartEarly.keyup( function () {  
        this.value = this.value.replace( /[^0-9\.]/g, '' ); 
    } );
    recordEndLate.keyup( function () {  
        this.value = this.value.replace( /[^0-9\.]/g, '' ); 
    } );
    recordStartEarly.change( function( event ) {
        var value = parseInt( $( '#program_details input[name="record_start_early"]' ).val() );
        if ( isNaN( $( '#program_details input[name="record_start_early"]' ).val() ) || value < 0 )
        {
            $( '#program_details input[name="record_start_early"]' ).val( 0 );
        }
        else if ( value > 60 )
        {
            $( '#program_details input[name="record_start_early"]' ).val( 60 );
        }
    } );
    recordEndLate.change( function( event ) {
        var value = parseInt( $( '#program_details input[name="record_end_late"]' ).val() );
        if ( isNaN( $( '#program_details input[name="record_end_late"]' ).val() ) || value < 0 )
        {
            $( '#program_details input[name="record_end_late"]' ).val( 0 );
        }
        else if ( value > 60 )
        {
            $( '#program_details input[name="record_end_late"]' ).val( 60 );
        }
    } );

    recordRecord.unbind( "click" );
    recordRecord.click( function( event ) {
        _createSchedule();
        event.preventDefault();
    } );
    recordRemove.unbind( "click" );
    recordRemove.click( function( event ) {
        _removeSchedule();
        event.preventDefault();
    } );

    $( ".program_details_section" ).css( "display", "none" );
    $( ".program_details_record" ).css( "display", "block" );
}

function _updateRecordingSchedulesSelection( schedule )
{
    var recordSchedules = $( '#program_details select[name="record_schedules"]' );

    scheduleId = parseInt( recordSchedules.val() );
    if ( scheduleId == -1 || !(scheduleId in _schedules) )
    {
        var epgId     = _currentEpgProgram.getEpgId();
        var channelId = "-1";
        for ( var id in _channels )
        {
            if ( _channels[id].getEpgId() == epgId )
            {
                channelId = id;
                break;
            }
        }

        _currentSchedule = new AminoPVRSchedule();
        _currentSchedule.setType                ( _currentSchedule.SCHEDULE_TYPE_ONCE );
        _currentSchedule.setChannelId           ( channelId );
        _currentSchedule.setStartTime           ( _currentEpgProgram.getStartTime() );
        _currentSchedule.setEndTime             ( _currentEpgProgram.getEndTime() );
        _currentSchedule.setTitle               ( _currentEpgProgram.getTitle() );
        _currentSchedule.setStartEarly          ( 0 );
        _currentSchedule.setEndLate             ( 0 );
        _currentSchedule.setPreferHd            ( false );
        _currentSchedule.setPreferUnscrambled   ( false );
        _currentSchedule.setDupMethod           ( _currentSchedule.DUPLICATION_METHOD_NONE );
        _currentSchedule.setInactive            ( false );
    }
    else
    {
        _currentSchedule = _schedules[scheduleId];
    }

    _updateRecordingFields( _currentSchedule );
}

function _updateRecordingFields( schedule )
{
    var recordChannel           = $( '#program_details select[name="record_channel"]' );
    var recordType              = $( '#program_details select[name="record_type"]' );
    var recordStartTime         = $( '#program_details input[name="record_starttime"]' );
    var recordEndTime           = $( '#program_details input[name="record_endtime"]' );
    var recordTitle             = $( '#program_details input[name="record_title"]' );
    var recordDupMethod         = $( '#program_details select[name="record_duplicate_method"]' );
    var recordStartEarly        = $( '#program_details input[name="record_start_early"]' );
    var recordEndLate           = $( '#program_details input[name="record_end_late"]' );
    var recordPreferHd          = $( '#program_details input[name="record_prefer_hd"]' );
    var recordPreferUnscrambled = $( '#program_details input[name="record_prefer_unscrambled"]' );
    var recordInactive          = $( '#program_details input[name="record_inactive"]' );
    var recordRecord            = $( '#program_details input[name="record_record"]' );
    var recordRemove            = $( '#program_details input[name="record_remove"]' );

    var dupMethod = [];
    if ( schedule.getDupMethod() & schedule.DUPLICATION_METHOD_TITLE )
    {
        dupMethod.push( schedule.DUPLICATION_METHOD_TITLE );
    }
    if ( schedule.getDupMethod() & schedule.DUPLICATION_METHOD_SUBTITLE )
    {
        dupMethod.push( schedule.DUPLICATION_METHOD_SUBTITLE );
    }
    if ( schedule.getDupMethod() & schedule.DUPLICATION_METHOD_DESCRIPTION )
    {
        dupMethod.push( schedule.DUPLICATION_METHOD_DESCRIPTION );
    }
    if ( dupMethod.length == 0 )
    {
        dupMethod.push( schedule.DUPLICATION_METHOD_NONE );
    }

    recordChannel.val( schedule.getChannelId() );
    recordStartTime.val( schedule.getStartTime()._toLocalJSON() );
    recordEndTime.val( schedule.getEndTime()._toLocalJSON() );
    recordTitle.val( schedule.getTitle() );
    recordDupMethod.val( dupMethod );
    recordStartEarly.val( schedule.getStartEarly() );
    recordEndLate.val( schedule.getEndLate() );
    recordPreferHd.prop( "checked", schedule.getPreferHd() );
    recordPreferUnscrambled.prop( "checked", schedule.getPreferUnscrambled() );
    recordInactive.prop( "checked", schedule.getInactive() );

    if ( schedule.getId() == -1 )
    {
        recordRemove.attr( "disabled", "disabled" );
    }
    else
    {
        recordRemove.removeAttr( "disabled" );
    }

    _updateRecordingMatches();
}

function _updateRecordingMatches()
{
    if ( !_scheduleMatchRequestBusy )
    {
        _getScheduleFromElements();

        _scheduleMatchRequestBusy = true;

        _currentSchedule.getMatches( null, function( status, context, matchedPrograms ) { _updateRecordingMatchesCallback( status, context, matchedPrograms ); }, true );
    }
}

function _updateRecordingMatchesCallback( status, context, matchedRecordings )
{
    if ( status )
    {
        try
        {
            var matchedRecordingList = "List:<br/>";
            for ( var i in matchedRecordings )
            {
                matchedRecordingList += matchedRecordings[i].getStartTime() + " - " + matchedRecordings[i].getTitle() + " from " + matchedRecordings[i].getChannelName() + "<br />";
            }

            $( "#program_details .program_details_record_matches" )[0].innerHTML = matchedRecordingList;

            logger.info( __module, "_updateRecordingMatchesCallback: Downloaded matched recording list" );
        }
        catch ( e )
        {
            logger.error( __module, "_updateRecordingMatchesCallback: exception: " + e );
        }
    }

    _scheduleMatchRequestBusy = false;
}

function _getScheduleFromElements()
{
    var recordChannel           = $( '#program_details select[name="record_channel"]' );
    var recordType              = $( '#program_details select[name="record_type"]' );
    var recordStartTime         = $( '#program_details input[name="record_starttime"]' );
    var recordEndTime           = $( '#program_details input[name="record_endtime"]' );
    var recordTitle             = $( '#program_details input[name="record_title"]' );
    var recordDupMethod         = $( '#program_details select[name="record_duplicate_method"]' );
    var recordStartEarly        = $( '#program_details input[name="record_start_early"]' );
    var recordEndLate           = $( '#program_details input[name="record_end_late"]' );
    var recordPreferHd          = $( '#program_details input[name="record_prefer_hd"]' );
    var recordPreferUnscrambled = $( '#program_details input[name="record_prefer_unscrambled"]' );
    var recordInactive          = $( '#program_details input[name="record_inactive"]' );

    dupMethod = 0;
    for ( var i in recordDupMethod.val() )
    {
        dupMethod += parseInt( recordDupMethod.val()[i] );
    }

    _currentSchedule.setType                ( parseInt( recordType.val() ) );
    _currentSchedule.setChannelId           ( parseInt( recordChannel.val() ) );
    _currentSchedule.setStartTime           ( new Date( recordStartTime.val() )._toUTC() );
    _currentSchedule.setEndTime             ( new Date( recordEndTime.val() )._toUTC() );
    _currentSchedule.setTitle               ( recordTitle.val() );
    _currentSchedule.setStartEarly          ( parseInt( recordStartEarly.val() ) );
    _currentSchedule.setEndLate             ( parseInt( recordEndLate.val() ) );
    _currentSchedule.setPreferHd            ( recordPreferHd.is( ":checked" ) ? true : false );
    _currentSchedule.setPreferUnscrambled   ( recordPreferUnscrambled.is( ":checked" ) ? true : false );
    _currentSchedule.setDupMethod           ( dupMethod );
    _currentSchedule.setInactive            ( recordInactive.is( ":checked" ) ? true : false );
}

function _createSchedule()
{
    _getScheduleFromElements();
    if ( _currentSchedule.addToDb() )
    {
        logger.warning( __module, "Created schedule with id=" + _currentSchedule.getId() );
    }
    else
    {
        logger.error( __module, "Unable to create scehdule" );
    }

    var requestContext = {};
    requestContext["callback"] = function() { ProgramDetailsRecord() };

    aminopvr.getScheduleList( requestContext, function( status, context, schedules ) { _getScheduleListCallback( status, context, schedules ); } );
}

function _removeSchedule()
{
    _getScheduleFromElements();
    if ( _currentSchedule.deleteFromDb() )
    {
        logger.warning( __module, "Deleted schedule with id=" + _currentSchedule.getId() );
    }
    else
    {
        logger.error( __module, "Unable to delete schedule" );
    }

    var requestContext = {};
    requestContext["callback"] = function() { ProgramDetailsRecord() };
    
    aminopvr.getScheduleList( requestContext, function( status, context, schedules ) { _getScheduleListCallback( status, context, schedules ); } );
}

$( function() {
    Init();
} );
