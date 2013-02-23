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

    this.DefaultKeys = function( keys ) { DebugLog( "ASTBClass.DefaultKeys( " + keys + " )" ); };
    this.WithChannels = function( channels ) { DebugLog( "ASTBClass.WithChannels( " + channels + " )" ); };
    this.SetMouseState = function( state ) { DebugLog( "ASTBClass.SetMouseState( " + state + " )" ); };
    this.SetKeyFunction = function( key, func ) { DebugLog( "ASTBClass.SetKeyFunction( " + key + ", " + func + " )" ); };
    this.GetConfig = function( key )
    {
        var config = "";

        DebugLog( "ASTBClass.GetConfig( " + key + " )" );

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
        DebugLog( "ASTBClass.GetSystemModel()" );
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
        DebugLog( "ASTBClass.GetPowerState()" );
        return 4;
    };
    this.SetPowerState = function( state )
    {
        DebugLog( "ASTBClass.SetPowerState( " + state + " )" );
        this.powerState = state;
    };
    this.Reboot = function() { DebugLog( "ASTBClass.Reboot()" ); };
    this.Upgrade = function( aa, bb ) { DebugLog( "ASTBClass.Upgrade( " + aa + ", " + bb + " )" ); };
    this.SetLEDState = function( led, state ) {};
    this.DebugString = function( debug ) { DebugLog( "ASTBClass.DebugString( " + debug + " )" ); };
    this.ErrorString = function( error ) { DebugLog( "ASTBClass.ErrorString( " + error + " )" ); };
    this.SetConfig = function( key, value, cc ) { DebugLog( "ASTBClass.SetConfig( " + key + ", " + value + ", " + cc + " )" ); };
    this.CommitConfig = function() { DebugLog( "ASTBClass.CommitConfig()" ); };
    this.GetIPAddress = function() { DebugLog( "ASTBClass.GetIPAddress()" ); };
    this.GetSystemManufacturer = function() { DebugLog( "ASTBClass.GetSystemManufacturer()" ); };
    this.GetHardwareVersion = function() { DebugLog( "ASTBClass.GetHardwareVersion()" ); };
    this.GetSoftwareVersion = function()
    {
        return "0.18.6-Ax3x-opera9";
    };
    this.GetSystemInfo = function()
    {
        return "<xml><aminoVersion>0.18.6-Ax3x-opera9</aminoVersion><aminoCVersion>0.18.6-Ax3x-opera9</aminoCVersion><oemVersion>zt6-ax3x-0.18.6.1</oemVersion></xml>";
    };
    this.GetSerialNumber = function() { DebugLog( "ASTBClass.GetSerialNumber()" ); };
}

function VideoDisplayClass()
{
    this.SetChromaKey = function( key ) { DebugLog( "VideoDisplayClass.SetChromaKey( " + key + " )" ); };
    this.SetAlphaLevel = function( level ) { DebugLog( "VideoDisplayClass.SetAlphaLevel( " + level + " )" ); };
    this.RetainMouseState = function( state ) { DebugLog( "VideoDisplayClass.RetainMouseState( " + state + " )" ); };
    this.RetainAlphaLevel = function( level ) { DebugLog( "VideoDisplayClass.RetainAlphaLevel( " + level + " )" ); };
    this.SetAVAspectSwitching = function( switching ) { DebugLog( "VideoDisplayClass.SetAVAspectSwitching( " + switching + " )" ); };
    this.SetAVAspect = function( aspect ) { DebugLog( "VideoDisplayClass.SetAVAspect( " + aspect + " )" ); };
    this.SetSubtitles = function( aa, bb ) { DebugLog( "VideoDisplayClass.SetSubtitles( " + aa + ", " + bb + " )" ); };
    this.SetTeletextFullscreen = function( fullscreen ) { DebugLog( "VideoDisplayClass.SetTeletextFullscreen( " + fullscreen + " )" ); };
    this.SetOutputFmt = function( format ) { DebugLog( "VideoDisplayClass.SetOutputFmt( " + format + " )" ); };
    this.SetAspect = function( aspect ) { DebugLog( "VideoDisplayClass.SetAspect( " + aspect + " )" ); };
    this.SetOutputResolution = function( resolution ) { DebugLog( "VideoDisplayClass.SetOutputResolution( " + resolution + " )" ); };
    this.SetPreferredHDRes = function( resolution ) { DebugLog( "VideoDisplayClass.SetPreferredHDRes( " + resolution + " )" ); };
}

function BrowserClass()
{
    this.SetToolbarState = function( state ) { DebugLog( "BrowserClass.SetToolbarState( " + state + " )" ); };
    this.FrameLoadResetsState = function( state ) { DebugLog( "BrowserClass.FrameLoadResetsState( " + state + " )" ); };
    this.Lower = function() { DebugLog( "BrowserClass.Lower()" ); };
    this.Raise = function() { DebugLog( "BrowserClass.Raise()" ); };
    this.Action = function( action ) { DebugLog( "BrowserClass.Action( " + action + " )" ); };
}

function AVMediaClass()
{
    this.onEvent = null;
    this.Event   = 0;

    this.Kill = function() { DebugLog( "AVMedia.Kill()" ); };
    this.Play = function( url ) { DebugLog( "AVMedia.Play( " + url + " )" ); };
    this.Pause = function() { DebugLog( "AVMedia.Play()" ) };
    this.Continue = function() { DebugLog( "AVMedia.Continue()" ) };
    this.GetMSecPosition = function() { return 0; };
    this.SetMSecPosition = function( pos ) { return pos; };
    this.SetSpeed = function( speed ) { DebugLog( "AVMedia.SetSpeed( " + speed + " )" ); };
    this.GetCurrentSpeed = function() { DebugLog( "AVMedia.GetCurrentSpeed()" ); return 0; };
    this.SetAudioPID = function( pid ) { DebugLog( "AVMedia.SetAudioPID( " + pid + " )" ); };
    this.SetPrimarySubtitleLanguage = function( lang, bb ) { DebugLog( "AVMedia.SetPrimarySubtitleLanguage( " + lang + ", " + bb + " )" ); };
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

                        asset.marker = responseItem.marker;

                        DebugLog( "RecordingAsset.ReadMeta: onreadystatechange: read meta data: marker=" + responseItem.marker );
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
        DebugLog( "RecordingAsset.WriteMeta( " + meta + " )" );

        var meta = eval( "(" + meta + ")" );
        this.marker = meta.marker;

        var recordingRequest = new XMLHttpRequest();

        recordingRequest.onreadystatechange = function()
        {
            if ( this.readyState == 4 )
            {
                if ( this.status == 200 )
                {
                    DebugLog( "RecordingAsset.WriteMeta: onreadystatechange: saved meta data" );
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

    this.GetPltInfo = function() { return "OK"; };
    this.GetStorageInfo = function()
    {
        if ( this.storage_info == null )
        {
            var pvr             = this;
            var storageRequest = new XMLHttpRequest();

            DebugLog( "PVRClass.GetStorageInfo: Downloading storage info" );

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

                            pvr.storage_info               = new StorageInfo;
                            pvr.storage_info.availableSize = responseItem["available_size"];
                            pvr.storage_info.totalSize     = responseItem["total_size"];

                            DebugLog( "PVRClass.GetStorageInfo: onreadystatechange: Downloaded storage info" );
                        }
                        catch ( e )
                        {
                            DebugLog( "PVRClass.GetStorageInfo: onreadystatechange: exception: " + e );
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

            DebugLog( "PVRClass.GetAssetIdList: Downloading recording list" );

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

                            for ( var row in responseItem )
                            {
                                asset                = new RecordingAsset;
                                asset.assetId        = responseItem[row]["id"];
                                asset.title          = responseItem[row]["title"];
                                asset.startTime      = responseItem[row]["start_time"];
                                asset.duration       = responseItem[row]["end_time"] - responseItem[row]["start_time"];
                                asset.viewingControl = 12;
                                asset.position       = 0;
                                asset.url            = "src=" + responseItem[row]["url"] + ";servertype=mediabase";
                                asset.marker         = responseItem[row]["marker"];

                                if ( responseItem[row]["subtitle"] != "" )
                                {
                                    asset.title += ": " + responseItem[row]["subtitle"];
                                }

                                pvr.recordings[asset.assetId] = asset;
                                pvr.recording_ids[i] = asset.assetId;
                                i++;
                            }

                            pvr.recording_ids.count = i - 1;

                            DebugLog( "PVRClass.GetAssetIdList: onreadystatechange: Downloaded recording list; count = " + pvr.recording_ids.count );
                        }
                        catch ( e )
                        {
                            DebugLog( "PVRClass.GetAssetIdList: onreadystatechange: exception: " + e );
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

            DebugLog( "PVRClass.GetScheduleList: Downloading schedule list" );

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

                            for ( var row in responseItem )
                            {
                                schedItem                = new ScheduleItem;
                                schedItem.title          = responseItem[row]["title"];
                                schedItem.startTime      = responseItem[row]["start_time"];
                                schedItem.endTime        = responseItem[row]["end_time"];
                                schedItem.viewingControl = responseItem[row]["viewing_control"];
                                schedItem.active         = responseItem[row]["active"];

                                pvr.schedule_list[i] = schedItem;
                                i++;
                            }

                            pvr.schedule_list.count = i - 1;

                            DebugLog( "PVRClass.GetScheduleList: onreadystatechange: Downloaded schedule list; count = " + pvr.schedule_list.count );
                        }
                        catch ( e )
                        {
                            DebugLog( "PVRClass.GetScheduleList: onreadystatechange: exception: " + e );
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
                DebugLog( "PVRClass.AddSchedule.onreadystatechange: done: " + this.responseText );
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
    DebugLog( e );
}
