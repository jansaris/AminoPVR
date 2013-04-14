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

var __module = "stub."

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
    this.Pause = function() { logger.info( this.__module(), "Play()" ) };
    this.Continue = function() { logger.info( this.__module(), "Continue()" ) };
    this.GetMSecPosition = function() { return 0; };
    this.SetMSecPosition = function( pos ) { return pos; };
    this.SetSpeed = function( speed ) { logger.info( this.__module(), "SetSpeed( " + speed + " )" ); };
    this.GetCurrentSpeed = function() { logger.info( this.__module(), "GetCurrentSpeed()" ); return 0; };
    this.SetAudioPID = function( pid ) { logger.info( this.__module(), "SetAudioPID( " + pid + " )" ); };
    this.SetPrimarySubtitleLanguage = function( lang, bb ) { logger.info( this.__module(), "SetPrimarySubtitleLanguage( " + lang + ", " + bb + " )" ); };
}

function StorageInfo()
{
    this.availableSize = 0;
    this.totalSize = 0;
}

function ScheduleItem()
{
    this.startTime = 0;
    this.endTime = 0;
    this.url = "";
    this.title = "";
    this.streamId = "";
    this.active = false;
    this.viewingControl = 0;
}

function RecordingAsset()
{
    this.assetId = 0;
    this.title = "";
    this.startTime = 0;
    this.duration = 0;
    this.viewingControl = 0;
    this.url = "";
    this.position = 0;
    this.marker = -1;

    this.__module = function()
    {
        return "stub." + this.constructor.name;
    };
    this.ReadMeta = function()
    {
        if ( this.marker == -1 )
        {
            var asset = this;

            var recordingRequest = new XMLHttpRequest();

            recordingRequest.onreadystatechange = function()
            {
                if ( this.readyState == 4 )
                {
                    if ( this.status == 200 )
                    {
                        var responseItem = eval( '(' + this.responseText + ')' );

						if ( repsonseItem["status"] == "success" )
						{
                        	asset.marker = responseItem["data"]["marker"];

                        	logger.info( this.__module(), "ReadMeta: onreadystatechange: read meta data: marker=" + responseItem["data"]["marker"] );
                        }
                    }
                }
            };

            recordingRequest.open( "GET", "/aminopvr/api/getRecordingMeta?id=" + this.assetId, false );
            recordingRequest.send();
        }

        return "{'marker':" + this.marker + "}";
    }
    this.WriteMeta = function( meta )
    {
        logger.info( this.__module(), "WriteMeta( " + meta + " )" );

        var meta = eval( "(" + meta + ")" );
        this.marker = meta.marker;

        var recordingRequest = new XMLHttpRequest();

        recordingRequest.onreadystatechange = function()
        {
            if ( this.readyState == 4 )
            {
                if ( this.status == 200 )
                {
                    logger.info( this.__module(), "WriteMeta: onreadystatechange: saved meta data" );
                }
            }
        };

        recordingRequest.open( "GET", "/aminopvr/api/setRecordingMeta?id=" + this.assetId + "&marker=" + this.marker, false );
        recordingRequest.send();
    }
}

function PVRClass()
{
    this.recording_ids = [];
    this.recordings    = []

    this.recording_ids[0]    = -1;
    this.recording_ids.count = 0;

    this.schedule_list       = [];
    this.schedule_list[0]    = "";
    this.schedule_list.count = 0;

    this.storage_info        = null;

    this.__module = function()
    {
        return "stub." + this.constructor.name;
    };
    this.GetPltInfo = function() { return "OK"; };
    this.GetStorageInfo = function()
    {
        if ( this.storage_info == null )
        {
            var pvr             = this;
            var storageRequest = new XMLHttpRequest();

            logger.info( this.__module(), "GetStorageInfo: Downloading storage info" );

            storageRequest.onreadystatechange = function()
            {
                if ( this.readyState == 4 )
                {
                    if ( this.status == 200 )
                    {
                        try
                        {
                            var responseItem = eval( '(' + this.responseText + ')' );
                            var i = 1;

							if ( responseItem["status"] == "success" )
							{
                            	pvr.storage_info               = new StorageInfo;
                            	pvr.storage_info.availableSize = responseItem["data"]["available_size"];
                            	pvr.storage_info.totalSize     = responseItem["data"]["total_size"];

                            	logger.info( this.__module(), "GetStorageInfo: onreadystatechange: Downloaded storage info" );
                            }
                            else
                            {
                            	logger.error( this.__module(), "GetStorageInfo: onreadystatechange: Failed to get storage info: " + responseItem["status"] )
                            }
                        }
                        catch ( e )
                        {
                            logger.error( this.__module(), "GetStorageInfo: onreadystatechange: exception: " + e );
                        }
                    }
                }
            };
            storageRequest.open( "GET", "/aminopvr/api/getStorageInfo", false );
            storageRequest.send();
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
        if ( this.recording_ids.count == 0 )
        {
            var pvr               = this;
            var recordingsRequest = new XMLHttpRequest();

            logger.info( this.__module(), "GetAssetIdList: Downloading recording list" );

            recordingsRequest.onreadystatechange = function()
            {
                if ( this.readyState == 4 )
                {
                    if ( this.status == 200 )
                    {
                        try
                        {
                            var responseItem = eval( '(' + this.responseText + ')' );
                            var i = 1;

							if ( responseItem["status"] == "success" )
							{
	                            for ( var row in responseItem["data"] )
	                            {
	                                asset                = new RecordingAsset;
	                                asset.assetId        = responseItem["data"][row]["id"];
	                                asset.title          = responseItem["data"][row]["title"];
	                                asset.startTime      = responseItem["data"][row]["start_time"];
	                                asset.duration       = responseItem["data"][row]["end_time"] - responseItem["data"][row]["start_time"];
	                                asset.viewingControl = 12;
	                                asset.position       = 0;
	                                asset.url            = "src=" + responseItem["data"][row]["url"] + ";servertype=mediabase";
	                                asset.marker         = responseItem["data"][row]["marker"];

	                                if ( responseItem["data"][row]["subtitle"] != "" )
	                                {
	                                    asset.title += ": " + responseItem["data"][row]["subtitle"];
	                                }

	                                pvr.recordings[asset.assetId] = asset;
	                                pvr.recording_ids[i] = asset.assetId;
	                                i++;
	                            }

	                            pvr.recording_ids.count = i - 1;
	                        }

                            logger.info( this.__module(), "GetAssetIdList: onreadystatechange: Downloaded recording list; count = " + pvr.recording_ids.count );
                        }
                        catch ( e )
                        {
                            logger.error( this.__module(), "GetAssetIdList: onreadystatechange: exception: " + e );
                        }
                    }
                }
            };
            recordingsRequest.open( "GET", "/aminopvr/api/getRecordingList", false );
            recordingsRequest.send();
        }

        return this.recording_ids;
    };
    this.GetScheduleList = function()
    {
        if ( this.schedule_list.count == 0 )
        {
            var pvr             = this;
            var scheduleRequest = new XMLHttpRequest();

            logger.info( this.__module(), "GetScheduleList: Downloading schedule list" );

            scheduleRequest.onreadystatechange = function()
            {
                if ( this.readyState == 4 )
                {
                    if ( this.status == 200 )
                    {
                        try
                        {
                            var responseItem = eval( '(' + this.responseText + ')' );
                            var i = 1;

							if ( responseItem["status"] == "success" )
							{
	                            for ( var row in responseItem["data"] )
    	                        {
        	                        schedItem                = new ScheduleItem;
            	                    schedItem.title          = responseItem["data"][row]["title"];
                	                schedItem.startTime      = responseItem["data"][row]["start_time"];
                    	            schedItem.endTime        = responseItem["data"][row]["end_time"];
                        	        schedItem.viewingControl = responseItem["data"][row]["viewing_control"];
                            	    schedItem.active         = responseItem["data"][row]["active"];

	                                pvr.schedule_list[i] = schedItem;
    	                            i++;
        	                    }

            	                pvr.schedule_list.count = i - 1;
            	            }

                            logger.info( this.__module(), "GetScheduleList: onreadystatechange: Downloaded schedule list; count = " + pvr.schedule_list.count );
                        }
                        catch ( e )
                        {
                            logger.error( this.__module(), "GetScheduleList: onreadystatechange: exception: " + e );
                        }
                    }
                }
            };
            scheduleRequest.open( "GET", "/aminopvr/api/getScheduleList", false );
            scheduleRequest.send();
        }

        return this.schedule_list;
    };
    this.DeleteAsset = function( assetId ) { return "OK"; };
    this.AddSchedule = function( url, titleId, starttime, endtime, aa )
    {
        var schedule = "{\"url\":\"" + url + "\",\"titleid\":\"" + titleId + "\",\"starttime\":" + starttime + ",\"endtime\":" + endtime + ",\"aa\":\"" + aa + "\"}";

        var scheduleRequest = new XMLHttpRequest();
        scheduleRequest.onreadystatechange = function()
        {
            if ( (this.readyState == 4) && (this.status == 200) )
            {
                logger.info( this.__module(), "AddSchedule.onreadystatechange: done: " + this.responseText );
            }
        };
        scheduleRequest.open( "POST", "/aminopvr/api/addSchedule", false );
        scheduleRequest.setRequestHeader( "Content-type", "application/x-www-form-urlencoded" );
        scheduleRequest.send( "schedule=" + encodeURIComponent( schedule ) );

        return "OK";
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
