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

function ASTBClass()
{
    this.powerState = 0;

    this.__module = function()
    {
        return "stub." + this.constructor.name;
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
    this.Reboot = function() { logger.info( this.__module(), "Reboot()" ); };
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
        return "stub." + this.constructor.name;
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
        return "stub." + this.constructor.name;
    };
    this.SetToolbarState = function( state ) { logger.info( this.__module(), "SetToolbarState( " + state + " )" ); };
    this.FrameLoadResetsState = function( state ) { logger.info( this.__module(), "FrameLoadResetsState( " + state + " )" ); };
    this.Lower = function() { logger.info( this.__module(), "Lower()" ); };
    this.Raise = function() { logger.info( this.__module(), "Raise()" ); };
    this.Action = function( action ) { logger.info( this.__module(), "Action( " + action + " )" ); };
}

function AVMediaClass()
{
    this.onEvent = null;
    this.Event   = 0;

    this.__module = function()
    {
        return "stub." + this.constructor.name;
    };
    this.Kill = function() { logger.info( this.__module(), "Kill()" ); };
    this.Play = function( url ) { logger.info( this.__module(), "Play( " + url + " )" ); };
    this.Pause = function() { logger.info( this.__module(), "Play()" ); };
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
        return "stub." + this.constructor.name;
    };
    this.ReadMeta = function()
    {
        var self    = this;
        var context = {};
        context["asset"] = this;

        this._recording.readMarker( context, function( status, context, data )
        {
            asset = context["asset"];
            if ( status )
            {
                asset.marker = data;

                logger.info( self.__module(), "ReadMeta.callback: read meta data: marker=" + asset.marker );
            }
        }, false );

        return "{'marker':" + this.marker + "}";
    };
    this.WriteMeta = function( meta )
    {
        logger.info( this.__module(), "WriteMeta( " + meta + " )" );

        var meta    = eval( "(" + meta + ")" );
        this.marker = meta.marker;

        var self    = this;
        var context = {};

        this._recording.writeMarker( this.marker, context, function( status, context, data )
        {
            if ( status )
            {
                logger.info( self.__module(), "WriteMeta.callback: saved meta data" );
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
        return "stub." + this.constructor.name;
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
            request.send( "GET", "/aminopvr/api/getStorageInfo", false );
        }

        return this.storage_info;
    };
    this.GetDeviceInfo = function()
    {
        return "{'id':'mythtv'}";
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
                var i    = 1;
                var host = location.protocol + "//" + location.host;
//                var host = "rtsp://" + location.hostname + ":8554/";

                logger.warning( this.__module(), "_recordingListCallback.callback: host=" + host );

                for ( var row in recordings )
                {
                    recording            = recordings[row];
                    asset                = new RecordingAsset;
                    asset.assetId        = recording.getId();
                    asset.title          = recording.getFullTitle();
                    asset.startTime      = recording.getStartTime();
                    asset.duration       = recording.getEndTime() - recording.getStartTime();
                    asset.viewingControl = 12;
                    asset.position       = 0;
                    asset.url            = "src=" + host + recording.getUrl() + ";servertype=mediabase";
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
                        schedItem.startTime         = recording.getStartTime();
                        schedItem.endTime           = recording.getEndTime();
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

        var program = aminopvr.getEpgProgramByOriginalId( programId );
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
                        schedule.setStartTime           ( startTime );
                        schedule.setEndTime             ( endTime );
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
