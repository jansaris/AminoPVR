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

function VLCClass()
{
    this._vlcObject = null;
    this._channels  = [];

    this.__module = function()
    {
        return this.constructor.name;
    };

    this._onLoad = function()
    {
        try
        {
            this._vlcObject = document.createElement( 'embed' );
            this._vlcObject.setAttribute( 'type',           'application/x-vlc-plugin' );
            this._vlcObject.setAttribute( 'pluginspage',    'http://www.videolan.org' );
            this._vlcObject.setAttribute( 'id',             'vlc' );
            this._vlcObject.setAttribute( 'controls',       'false' );
            this._vlcObject.setAttribute( 'width',          '100%' );
            this._vlcObject.setAttribute( 'height',         '100%' );
            this._vlcObject.style.left      = "0px";
            this._vlcObject.style.top       = "0px";
            this._vlcObject.style.position  = "absolute";
            this._vlcObject.style.zIndex    = "0";

            this._registerVLCEvent( 'MediaPlayerNothingSpecial',    this._handleEvents );
            this._registerVLCEvent( 'MediaPlayerOpening',           this._handleEvents );
            this._registerVLCEvent( 'MediaPlayerBuffering',         this._handleEvents );
            this._registerVLCEvent( 'MediaPlayerPlaying',           this._handleEvents );
            this._registerVLCEvent( 'MediaPlayerPaused',            this._handleEvents );
            this._registerVLCEvent( 'MediaPlayerForward',           this._handleEvents );
            this._registerVLCEvent( 'MediaPlayerBackward',          this._handleEvents );
            this._registerVLCEvent( 'MediaPlayerEncounteredError',  this._handleEvents );
            this._registerVLCEvent( 'MediaPlayerEndReached',        this._handleEvents );
            this._registerVLCEvent( 'MediaPlayerTimeChanged',       this._handleEvents );
            this._registerVLCEvent( 'MediaPlayerPositionChanged',   this._handleEvents );
            this._registerVLCEvent( 'MediaPlayerSeekableChanged',   this._handleEvents );
            this._registerVLCEvent( 'MediaPlayerPausableChanged',   this._handleEvents );

            document.body.appendChild( this._vlcObject );

            aminopvr.getChannelList( this, function( status, context, channels )
            {
                if ( status )
                {
                    try
                    {
                        for ( var i in channels )
                        {
                            var id = context._vlcObject.playlist.add( channels[i].getUrl(), channels[i].getName() );
                            context._channels.push( { url: channels[i].getUrl(), channel: channels[i], id: id } );
                        }
                    }
                    catch ( e )
                    {
                        logger.error( context.__module(), "_onLoad: setChannelList.callback: exception: " + e );
                    }
                }
            }, true );
        }
        catch ( e )
        {
            logger.error( this.__module(), "_onLoad: exception: " + e );
        }
    };

    this.play = function( url )
    {
        if ( this._vlcObject != null )
        {
            var urlParts    = url.split( ';' );
            var url         = urlParts[0].substring( 4 ).replace( 'rtsp://', '' ).replace( 'igmp://', '' ).replace( '/', '' );
            var ip          = url.split( ':' )[0];
            var port        = url.split( ':' )[1];
            var found       = false;

            for ( var i in this._channels )
            {
                if ( (this._channels[i].url.indexOf( ip ) != -1) && (this._channels[i].url.indexOf( port ) != -1) )
                {
                    logger.warning( this.__module(), "play: going to play playlist item: " + this._channels[i].id );
                    this._vlcObject.playlist.playItem( this._channels[i].id );
                    found = true
                    break;
                }
            }

            if ( !found )
            {
                var channel = aminopvr.getChannelByIpPort( ip, port );

                if ( channel != null )
                {
                    for ( var i in this._channels )
                    {
                        if ( this._channels[i].url == channel.getUrl() )
                        {
                            logger.warning( this.__module(), "play: adding url: " + url + " to list as playlist item: " + this._channels[i].id );
                            this._channels.push( { url: url, channel: channel, id: this._channels[i].id } );

                            logger.warning( this.__module(), "play: going to play playlist item: " + this._channels[i].id );
                            this._vlcObject.playlist.playItem( this._channels[i].id );
                            break;
                        }
                    }
                }
                else
                {
                    logger.error( this.__module(), "play: channel with ip: " + ip + " and port: " + port + " not found" );
                }
            }

            this._vlcObject.video.deinterlace.enable("yadif2x");
        }
    }

    this.stop = function()
    {
        if ( this._vlcObject != null )
        {
            this._vlcObject.playlist.stop();
        }
    }

    this._registerVLCEvent = function( event, handler )
    {
        if ( this._vlcObject )
        {
            if ( this._vlcObject.attachEvent )
            {
                // Microsoft
                this._vlcObject.attachEvent( event, handler );
            }
            else if ( this._vlcObject.addEventListener )
            {
                // Mozilla: DOM level 2
                this._vlcObject.addEventListener( event, handler, false );
            }
            else
            {
                // DOM level 0
                this._vlcObject["on" + event] = handler;
            }
        }
    };

    // event callback function for testing
    this._handleEvents = function( event )
    {
        if ( !event )
        {
            event = window.event; // IE
        }
        if ( event.target )
        {
            // Netscape based browser
            targ = event.target;
        }
        else if ( event.srcElement )
        {
            // ActiveX
            targ = event.srcElement;
        }
        else
        {
            // No event object, just the value
            logger.error( this.__module(), "_handleEvents: Event value" + event );
            return;
        }
        if ( targ.nodeType == 3 )   // defeat Safari bug
        {
            targ = targ.parentNode;
        }

        logger.error( this.__module(), "_handleEvents: Event " + event.type + " has fired from " + targ );
    };

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
}

function ASTBClass()
{
    this.powerState = 0;

    this.__module = function()
    {
        return "impl." + this.constructor.name;
    };
    this.DefaultKeys = function( keys ) { logger.info( this.__module(), "DefaultKeys( " + keys + " )" ); };
    this.WithChannels = function( channels ) { logger.info( this.__module(), "WithChannels( " + channels + " )" ); };
    this.SetMouseState = function( state ) { logger.info( this.__module(), "SetMouseState( " + state + " )" ); };
    this.SetKeyFunction = function( key, func ) { logger.info( this.__module(), "SetKeyFunction( " + key + ", " + func + " )" ); };
    this.GetConfig = function( key )
    {
        var config = "";

        logger.info( this.__module(), "GetConfig( " + key + " )" );

        switch ( key )
        {
            case "SETTINGS.DISPLAY_MODE":
                config = "widescreen";
                break;
        }

        return config;
    };
    this.GetSystemModel = function()
    {
        logger.info( this.__module(), "GetSystemModel()" );
        return "aminet130";
    };
    this.GetSystemSubmodel = function()
    {
//        return "aminet130m";
        return "M032";
    };
    this.GetMacAddress = function()
    {
        return "00:02:02:31:f7:4a";
    };
    this.GetPowerState = function()
    {
        logger.info( this.__module(), "GetPowerState()" );
        return 4;
    };
    this.SetPowerState = function( state )
    {
        logger.info( this.__module(), "SetPowerState( " + state + " )" );
        this.powerState = state;
    };
    this.Reboot = function()
    {
    	logger.info( this.__module(), "Reboot()" );
    	location.reload();
    };
    this.Upgrade = function( aa, bb ) { logger.info( this.__module(), "Upgrade( " + aa + ", " + bb + " )" ); };
    this.SetLEDState = function( led, state ) {};
    this.DebugString = function( debug ) { logger.info( this.__module(), "DebugString( " + debug + " )" ); };
    this.ErrorString = function( error ) { logger.info( this.__module(), "ErrorString( " + error + " )" ); };
    this.SetConfig = function( key, value, cc ) { logger.info( this.__module(), "SetConfig( " + key + ", " + value + ", " + cc + " )" ); };
    this.CommitConfig = function() { logger.info( this.__module(), "CommitConfig()" ); };
    this.GetIPAddress = function() { logger.info( this.__module(), "GetIPAddress()" ); };
    this.GetSystemManufacturer = function() { logger.info( this.__module(), "GetSystemManufacturer()" ); };
    this.GetHardwareVersion = function() { logger.info( this.__module(), "GetHardwareVersion()" ); };
    this.GetSoftwareVersion = function()
    {
        return "0.18.7a3-Ax3x-opera10";
    };
    this.GetSystemInfo = function()
    {
        return "<xml><aminoVersion>0.18.7a3-Ax3x-opera10</aminoVersion><aminoCVersion>0.18.7-Ax3x-opera10</aminoCVersion><oemVersion>zt6-ax3x-0.18.7a3.0</oemVersion></xml>";
    };
    this.GetSerialNumber = function() { logger.info( this.__module(), "GetSerialNumber()" ); };
}

function VideoDisplayClass()
{
    this.__module = function()
    {
        return "impl." + this.constructor.name;
    };
    this.SetChromaKey = function( key ) { logger.info( this.__module(), "SetChromaKey( " + key + " )" ); };
    this.SetAlphaLevel = function( level ) { logger.info( this.__module(), "SetAlphaLevel( " + level + " )" ); };
    this.RetainMouseState = function( state ) { logger.info( this.__module(), "RetainMouseState( " + state + " )" ); };
    this.RetainAlphaLevel = function( level ) { logger.info( this.__module(), "RetainAlphaLevel( " + level + " )" ); };
    this.SetAVAspectSwitching = function( switching ) { logger.info( this.__module(), "SetAVAspectSwitching( " + switching + " )" ); };
    this.SetAVAspect = function( aspect ) { logger.info( this.__module(), "SetAVAspect( " + aspect + " )" ); };
    this.SetSubtitles = function( aa, bb ) { logger.info( this.__module(), "SetSubtitles( " + aa + ", " + bb + " )" ); };
    this.SetTeletextFullscreen = function( fullscreen ) { logger.info( this.__module(), "SetTeletextFullscreen( " + fullscreen + " )" ); };
    this.SetOutputFmt = function( format ) { logger.info( this.__module(), "SetOutputFmt( " + format + " )" ); };
    this.SetAspect = function( aspect ) { logger.info( this.__module(), "SetAspect( " + aspect + " )" ); };
    this.SetOutputResolution = function( resolution ) { logger.info( this.__module(), "SetOutputResolution( " + resolution + " )" ); };
    this.SetPreferredHDRes = function( resolution ) { logger.info( this.__module(), "SetPreferredHDRes( " + resolution + " )" ); };
}

function BrowserClass()
{
    this.__module = function()
    {
        return "impl." + this.constructor.name;
    };
    this.SetToolbarState = function( state ) { logger.info( this.__module(), "SetToolbarState( " + state + " )" ); };
    this.FrameLoadResetsState = function( state ) { logger.info( this.__module(), "FrameLoadResetsState( " + state + " )" ); };
    this.Lower = function() { logger.info( this.__module(), "Lower()" ); };
    this.Raise = function() { logger.info( this.__module(), "Raise()" ); };
    this.Action = function( action ) { logger.info( this.__module(), "Action( " + action + " )" ); };
}

function AVMediaClass()
{
    this.vlc     = new VLCClass;
    this.onEvent = null;
    this.Event   = 0;

    this.__module = function()
    {
        return "impl." + this.constructor.name;
    };
    this.Kill = function()
    {
        logger.warning( this.__module(), "Kill()" );

        this.vlc.stop();
    };
    this.Play = function( url )
    {
    	logger.warning( this.__module(), "Play( " + url + " )" );

        this.vlc.play( url );
    };
    this.Pause = function() { logger.info( this.__module(), "Pause()" ); };
    this.Continue = function() { logger.info( this.__module(), "Continue()" ); };
    this.GetMSecPosition = function() { return 0; };
    this.SetMSecPosition = function( pos ) { return pos; };
    this.SetSpeed = function( speed ) { logger.info( this.__module(), "SetSpeed( " + speed + " )" ); };
    this.GetCurrentSpeed = function() { logger.info( this.__module(), "GetCurrentSpeed()" ); return 0; };
    this.SetAudioPID = function( pid ) { logger.info( this.__module(), "SetAudioPID( " + pid + " )" ); };
    this.SetPrimarySubtitleLanguage = function( lang, bb ) { logger.info( this.__module(), "SetPrimarySubtitleLanguage( " + lang + ", " + bb + " )" ); };
}

function StorageInfo()
{
    this.availableSize  = 0;
    this.totalSize      = 0;
}

function ScheduleItem()
{
    this.startTime      = 0;
    this.endTime        = 0;
    this.url            = "";
    this.title          = "";
    this.streamId       = "";
    this.active         = false;
    this.viewingControl = 0;
    this._schedule      = null;
}

function RecordingAsset()
{
    this.assetId        = 0;
    this.title          = "";
    this.startTime      = 0;
    this.duration       = 0;
    this.viewingControl = 0;
    this.url            = "";
    this.position       = 0;
    this.marker         = -1;
    this._recording     = null;

    this.__module = function()
    {
        return "impl." + this.constructor.name;
    };
    this.ReadMeta = function()
    {
        var self    = this;
        var context = {};
        context["asset"] = this;

        logger.info( this.__module(), "ReadMeta" );

        this._recording.readMarker( context, function( status, context, data )
        {
            asset = context["asset"];
            if ( status )
            {
                asset.marker = data;

                logger.info( self.__module(), "ReadMeta.callback: read meta data: marker=" + asset.marker );
            }
        }, false );

        return '{"marker":' + this.marker + '}';
    };
    this.WriteMeta = function( meta )
    {
        logger.warning( this.__module(), "WriteMeta( " + meta + " )" );

        var meta    = eval( "(" + meta + ")" );
        this.marker = meta.marker;

        var self    = this;
        var context = {};

        this._recording.writeMarker( this.marker, context, function( status, context, data )
        {
            if ( status )
            {
                logger.warning( self.__module(), "WriteMeta.callback: saved meta data" );
            }
        }, false );
    };
    this.Delete = function()
    {
        logger.info( this.__module(), "Delete()" );

        return this._recording.deleteFromDb();
    };
}

function PVRClass()
{
    this.recording_ids                  = [];
    this.recordings                     = [];

    this.recording_ids[0]               = -1;
    this.recording_ids.count            = 0;

    this.schedule_list                  = [];
    this.schedule_list.count            = 0;

    this.scheduled_recording_list       = [];
    this.scheduled_recording_list[0]    = "";
    this.scheduled_recording_list.count = 0;

    this.storage_info                   = null;

    this.__module = function()
    {
        return "impl." + this.constructor.name;
    };
    this.GetPltInfo = function() { return "OK"; };
    this.GetStorageInfo = function()
    {
        if ( this.storage_info == null )
        {
            logger.info( this.__module(), "GetStorageInfo: Downloading storage info" );

            var self    = this;
            var request = new JsonAjaxRequest();
            request.setCallback( function( status, context, data )
            {
                if ( status )
                {
                    try
                    {
                        self.storage_info               = new StorageInfo;
                        self.storage_info.availableSize = data["available_size"];
                        self.storage_info.totalSize     = data["total_size"];

                        logger.info( self.__module(), "GetStorageInfo.callback: Downloaded storage info" );
                    }
                    catch ( e )
                    {
                        logger.error( self.__module(), "GetStorageInfo.callback: exception: " + e );
                    }
                }
            } );
            request.send( "GET", "/api/getStorageInfo", false );
        }

        return this.storage_info;
    };
    this.GetDeviceInfo = function()
    {
        return "{'id':'AminoPVR'}";
    };
    this.GetDeviceStatus = function( deviceId )
    {
        return "{'state':'Ready'}";
    };
    this.GetAssetById = function( assetId )
    {
        var asset;
        if ( this.recordings.length && this.recordings[assetId] )
        {
            asset = this.recordings[assetId];
        }
        return asset;
    };
    this.GetAssetIdList = function()
    {
        logger.debug( this.__module(), "GetAssetIdList" );
        if ( this.recording_ids.count == 0 )
        {
            var self    = this;
            var context = {};

            aminopvr.getRecordingList( context, function( status, context, recordings ) { self._recordingListCallback( status, context, recordings ); }, false );
        }

        return this.recording_ids;
    };
    this._recordingListCallback = function( status, context, recordings )
    {
        if ( status )
        {
            try
            {
                var i             = 1;
                var host          = "/";
//                var host = location.protocol + "//" + location.host;
                var generalConfig = aminopvr.getGeneralConfig();
                if ( generalConfig != null )
                {
                    host = "rtsp://" + location.hostname + ":" + generalConfig.getRtspServerPort() + "/";
//                    host = "http://" + location.hostname + ":" + generalConfig.getServerPort() + "/";
                }

                logger.warning( this.__module(), "_recordingListCallback.callback: host=" + host );

                for ( var row in recordings )
                {
                    recording            = recordings[row];
                    asset                = new RecordingAsset;
                    asset.assetId        = recording.getId();
                    asset.title          = recording.getFullTitle();
                    asset.startTime      = Math.round( recording.getStartTime().getTime() / 1000 );
                    asset.duration       = Math.round( recording.getEndTime().getTime() / 1000 ) - asset.startTime;
                    asset.viewingControl = 12;
                    asset.position       = 0;
                    asset.url            = "src=" + host + recording.getFilename();// + ";servertype=mediabase";
//                    asset.url            = "src=" + host + "recordings/" + recording.getId();
                    asset.marker         = recording.getMarker();
                    asset._recording     = recording;
    
                    this.recordings[asset.assetId] = asset;
                    this.recording_ids[i]          = asset.assetId;
                    i++;
                }

                this.recording_ids.count = i - 1;

                logger.info( this.__module(), "_recordingListCallback: Downloaded recording list; count = " + this.recording_ids.count );
            }
            catch ( e )
            {
                logger.error( this.__module(), "_recordingListCallback: exception: " + e );
            }
        }
    };
    this.DeleteAsset = function( assetId )
    {
        var deleted = false;
        if ( this.recording_ids.count > 0 )
        {
            if ( this.recordings[assetId] )
            {
                var asset   = this.recordings[assetId];
                deleted     = asset.Delete();
                for ( var i = 0; i < this.recording_ids.length; i++ )
                {
                    if ( this.recording_ids[i] == assetId )
                    {
                        this.recording_ids.splice( i, 1 );
                        break;
                    }
                }
                for ( var i = 0; i < this.recordings.length; i++ )
                {
                    if ( this.recordings[i].assetId == assetId )
                    {
                        this.recordings.splice( i, 1 );
                        break;
                    }
                }
            }
        }
        return deleted ? "OK" : "ERR";
    };
    this.GetScheduleList = function()
    {
        logger.debug( this.__module(), "GetScheduleList" );
        if ( this.schedule_list.count == 0 )
        {
            var self    = this;
            var context = {};

            this.scheduled_recording_list       = [];
            this.scheduled_recording_list[0]    = "";
            this.scheduled_recording_list.count = 0;

            aminopvr.getScheduleList( context, function( status, context, schedules ) { self._scheduleListCallback( status, context, schedules ); }, false );
            aminopvr.getScheduledRecordingList( context, function( status, context, recordings ) { self._scheduledRecordingListCallback( status, context, recordings ); }, false );
        }

        return this.scheduled_recording_list;
    };
    this._scheduleListCallback = function( status, context, schedules )
    {
        if ( status )
        {
            try
            {
                this.schedule_list = schedules;

                logger.info( this.__module(), "_scheduleListCallback.callback: Downloaded schedule list; count = " + this.schedule_list.count );
            }
            catch ( e )
            {
                logger.error( this.__module(), "_scheduleListCallback: exception: " + e );
            }
        }
    };
    this._scheduledRecordingListCallback = function( status, context, recordings )
    {
        if ( status )
        {
            try
            {
                var i = 1;

                for ( var row in recordings )
                {
                    recording                   = recordings[row];
                    schedule                    = null;
                    for ( var scheduleIt in this.schedule_list )
                    {
                        if ( recording.getScheduleId() == this.schedule_list[scheduleIt].getId() )
                        {
                            schedule = this.schedule_list[scheduleIt];
                            break;
                        }
                    }

                    if ( schedule )
                    {
                        schedItem                   = new ScheduleItem;
                        schedItem.title             = recording.getFullTitle();
                        schedItem.startTime         = Math.round( recording.getStartTime().getTime() / 1000 );
                        schedItem.endTime           = Math.round( recording.getEndTime().getTime() / 1000 );
                        schedItem.viewingControl    = 12;
                        schedItem.active            = !(schedule.getInactive());
                        schedItem._schedule         = recording;

                        this.scheduled_recording_list[i] = schedItem;
                        i++;
                    }
                }

                this.scheduled_recording_list.count = i - 1;

                logger.info( this.__module(), "_scheduledRecordingListCallback.callback: Downloaded scheduled recording list; count = " + this.scheduled_recording_list.count );
            }
            catch ( e )
            {
                logger.error( this.__module(), "_scheduledRecordingListCallback: exception: " + e );
            }
        }
    };
    this.AddSchedule = function( url, titleId, startTime, endTime, aa )
    {
        var added       = false;
        var title       = titleId.split( "||[", 2 )[0];
        var programId   = titleId.split( "||[", 2 )[1];

        this.epgProgram = null;
        aminopvr.getEpgProgramByOriginalId( programId, null, function( status, context, schedules ) { self._epgProgramCallback( status, context, schedules ); }, false );

        var program = this.epgProgram;
        if ( program )
        {
            var urlRe    = /([a-z]{3,5}):\/\/([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}):([0-9]{1,5})(;.*)?/;
            var urlMatch = urlRe.exec( url );
            if ( urlMatch )
            {
                var ip   = urlMatch[2];
                var port = urlMatch[3];

                var channel = aminopvr.getChannelByIpPort( ip, port );
                if ( channel )
                {
                    // See if we already have a schedule to record this program
                    var schedule = aminopvr.getScheduleByTitleAndChannelId( title, channel.getId() );
                    if ( schedule )
                    {
                        var timeDiff        = startTime - Math.round( schedule.getStartTime().getTime() / 1000 );
                        var scheduleType    = schedule.getType();
                        if ( scheduleType != schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_DAY &&
                             scheduleType != schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK )
                        {
                            // If the time diff is a week, then we seem to want to record once every week 
                            if ( timeDiff >= (7 * 24 * 60 * 60) )
                            {
                                schedule.setType( schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK );
                            }
                            // If the time diff is a week, then we seem to want to record once every day 
                            else if ( timeDiff >= (1 * 24 * 60 * 60) )
                            {
                                schedule.setType( schedule.SCHEDULE_TYPE_TIMESLOT_EVERY_DAY );
                            }

                            schedule.addToDb();
                        }

                        added = true;

                        this.schedule_list       = [];
                        this.schedule_list.count = 0;
                    }
                    else
                    {
                        schedule = new AminoPVRSchedule();

                        schedule.setType                ( schedule.SCHEDULE_TYPE_ONCE );
                        schedule.setChannelId           ( channelId );
                        schedule.setStartTime           ( new Date( startTime * 1000 ) );
                        schedule.setEndTime             ( new Date( endTime * 1000 ) );
                        schedule.setTitle               ( title );
                        schedule.setPreferHd            ( true );
                        schedule.setPreferUnscrambled   ( false );
                        schedule.setDupMethod           ( schedule.DUPLICATION_METHOD_TITLE | schedule.DUPLICATION_METHOD_SUBTITLE );

                        added = schedule.addToDb();

                        this.schedule_list       = [];
                        this.schedule_list.count = 0;
                    }
                }
            }
        }

        return added ? "OK" : "ERR";
    };
    this._epgProgramCallback = function( status, context, epgProgram )
    {
        if ( status )
        {
            try
            {
                this.epgProgram = epgProgram;

                logger.info( this.__module(), "_epgProgramCallback: Downloaded epg program" );
            }
            catch ( e )
            {
                logger.error( this.__module(), "_epgProgramCallback: exception: " + e );
            }
        }
    };
    this.DeleteSchedule = function() { return "OK"; };
    this.RequestDeviceReformat = function( aa ) { return "OK"; };
    this.FormatDevice = function( aa ) { return "OK"; };
    this.StopRecording = function( aa ) { return "OK"; };
}

try
{
    if ( !window.ASTB )
    {
        window.ASTB = new ASTBClass;
    }
    if ( !window.VideoDisplay )
    {
        window.VideoDisplay = new VideoDisplayClass;
    }
    if ( !window.Browser )
    {
        window.Browser = new BrowserClass;
    }
    if ( !window.AVMedia )
    {
        window.AVMedia = new AVMediaClass;
    }
    if ( !window.PVR )
    {
        window.PVR = new PVRClass;
    }
}
catch ( e )
{
    logger.critical( e );
}
