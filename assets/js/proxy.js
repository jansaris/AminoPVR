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

var ASTBProxy;
var PVRProxy;
var AVMediaProxy;
var BrowserProxy;
var VideoDisplayProxy;

function ASTBProxyClass()
{
    this.__module = function()
    {
        return "proxy." + this.constructor.name;
    };
    this.DefaultKeys = function( keys )
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.DefaultKeys( keys );
            }
            logger.info( this.__module(), "DefaultKeys( " + keys + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "DefaultKeys: exception: " + e );
        }
    };
    this.WithChannels = function( channels )
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.WithChannels( channels );
            }
            logger.info( this.__module(), "WithChannels( " + channels + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "WithChannels: exception: " + e );
        }
    };
    this.SetMouseState = function( state )
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.SetMouseState( state );
            }
            logger.info( this.__module(), "SetMouseState( " + state + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetMouseState: exception: " + e );
        }
    };
    this.SetKeyFunction = function( key, func )
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.SetKeyFunction( key, func );
            }
            logger.info( this.__module(), "SetKeyFunction( " + key + ", " + func + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetKeyFunction: exception: " + e );
        }
    };
    this.GetConfig = function( key )
    {
        retval = "";
        try
        {
            if ( window.ASTB )
            {
                retval = window.ASTB.GetConfig( key );
            }
            logger.info( this.__module(), "GetConfig( " + key + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetConfig: exception: " + e );
        }
        return retval;
    };
    this.GetSystemModel = function()
    {
        retval = "";
        try
        {
            if ( window.ASTB )
            {
                retval = window.ASTB.GetSystemModel();
            }
            logger.info( this.__module(), "GetSystemModel() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetSystemModel: exception: " + e );
        }
        return retval;
    };
    this.GetSystemSubmodel = function()
    {
        retval = "";
        try
        {
            if ( window.ASTB )
            {
                retval = window.ASTB.GetSystemSubmodel();
            }
            logger.info( this.__module(), "GetSystemSubmodel() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetSystemSubmodel: exception: " + e );
        }
        return retval;
    };
    this.GetMacAddress = function()
    {
        retval = "";
        try
        {
            if ( window.ASTB )
            {
                retval = window.ASTB.GetMacAddress();
            }
            logger.info( this.__module(), "GetMacAddress() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetMacAddress: exception: " + e );
        }
        return retval;
    };
    this.GetPowerState = function()
    {
        retval = "";
        try
        {
            if ( window.ASTB )
            {
                retval = window.ASTB.GetPowerState();
            }
            logger.info( this.__module(), "GetPowerState() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetPowerState: exception: " + e );
        }
        return retval;
    };
    this.SetPowerState = function( state )
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.SetPowerState( state );
            }
            logger.info( this.__module(), "SetPowerState( " + state + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetPowerState: exception: " + e );
        }
    };
    this.Reboot = function()
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.Reboot();
            }
            logger.info( this.__module(), "Reboot()" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "Reboot: exception: " + e );
        }
    };
    this.Upgrade = function( aa, bb )
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.Upgrade( aa, bb );
            }
            logger.info( this.__module(), "Upgrade( " + aa + ", " + bb + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "Upgrade: exception: " + e );
        }
    };
    this.SetLEDState = function( led, state )
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.SetLEDState( led, state );
            }
//            logger.info( this.__module(), "SetLEDState( " + led + ", " + state + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetLEDState: exception: " + e );
        }
    };
    this.DebugString = function( debug )
    {
        logger.info( this.__module(), debug );
    };
    this.ErrorString = function( error )
    {
        logger.error( this.__module(), error );
    };
    this.SetConfig = function( key, value, cc )
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.SetConfig( key, value, cc );
            }
            logger.info( this.__module(), "SetConfig( " + key + ", " + value + ", " + cc + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetConfig: exception: " + e );
        }
    };
    this.CommitConfig = function()
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.CommitConfig();
            }
            logger.info( this.__module(), "CommitConfig()" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "CommitConfig: exception: " + e );
        }
    };
    this.GetIPAddress = function()
    {
        retval = "";
        try
        {
            if ( window.ASTB )
            {
                retval = window.ASTB.GetIPAddress();
            }
            logger.info( this.__module(), "GetIPAddress() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetIPAddress: exception: " + e );
        }
        return retval;
    };
    this.GetSystemManufacturer = function()
    {
        retval = "";
        try
        {
            if ( window.ASTB )
            {
                retval = window.ASTB.GetSystemManufacturer();
            }
            logger.info( this.__module(), "GetSystemManufacturer() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetSystemManufacturer: exception: " + e );
        }
        return retval;
    };
    this.GetHardwareVersion = function()
    {
        retval = "";
        try
        {
            if ( window.ASTB )
            {
                retval = window.ASTB.GetHardwareVersion();
            }
            logger.info( this.__module(), "GetHardwareVersion() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetHardwareVersion: exception: " + e );
        }
        return retval;
    };
    this.GetSoftwareVersion = function()
    {
        retval = "";
        try
        {
            if ( window.ASTB )
            {
                retval = window.ASTB.GetSoftwareVersion();
            }
            logger.info( this.__module(), "GetSoftwareVersion() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetSoftwareVersion: exception: " + e );
        }
        return retval;
    };
    this.GetSystemInfo = function()
    {
        retval = "";
        try
        {
            if ( window.ASTB )
            {
                retval = window.ASTB.GetSystemInfo();
            }
            logger.info( this.__module(), "GetSystemInfo() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetSystemInfo: exception: " + e );
        }
        return retval;
    };
    this.GetSerialNumber = function()
    {
        retval = "";
        try
        {
            if ( window.ASTB )
            {
                retval = window.ASTB.GetSerialNumber();
            }
            logger.info( this.__module(), "GetSerialNumber() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetSerialNumber: exception: " + e );
        }
        return retval;
    };
}

function VideoDisplayProxyClass()
{
    this.__module = function()
    {
        return "proxy." + this.constructor.name;
    };
    this.SetChromaKey = function( key )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.SetChromaKey( key );
            }
            logger.info( this.__module(), "SetChromaKey( " + key + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetChromaKey: exception: " + e );
        }
    };
    this.SetAlphaLevel = function( level )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.SetAlphaLevel( level );
            }
            logger.info( this.__module(), "SetAlphaLevel( " + level + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetAlphaLevel: exception: " + e );
        }
    };
    this.RetainMouseState = function( state )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.RetainMouseState( state );
            }
            logger.info( this.__module(), "RetainMouseState( " + state + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "RetainMouseState: exception: " + e );
        }
    };
    this.RetainAlphaLevel = function( level )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.RetainAlphaLevel( level );
            }
            logger.info( this.__module(), "RetainAlphaLevel( " + level + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "RetainAlphaLevel: exception: " + e );
        }
    };
    this.SetAVAspectSwitching = function( switching )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.SetAVAspectSwitching( switching );
            }
            logger.info( this.__module(), "SetAVAspectSwitching( " + switching + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetAVAspectSwitching: exception: " + e );
        }
    };
    this.SetAVAspect = function( aspect )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.SetAVAspect( aspect );
            }
            logger.info( this.__module(), "SetAVAspect( " + aspect + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetAVAspect: exception: " + e );
        }
    };
    this.SetSubtitles = function( aa, bb )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.SetSubtitles( aa, bb );
            }
            logger.info( this.__module(), "SetSubtitles( " + aa + ", " + bb + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetSubtitles: exception: " + e );
        }
    };
    this.SetTeletextFullscreen = function( fullscreen )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.SetTeletextFullscreen( fullscreen );
            }
            logger.info( this.__module(), "SetTeletextFullscreen( " + fullscreen + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetTeletextFullscreen: exception: " + e );
        }
    };
    this.SetOutputFmt = function( format )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.SetOutputFmt( format );
            }
            logger.info( this.__module(), "SetOutputFmt( " + format + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetOutputFmt: exception: " + e );
        }
    };
    this.SetAspect = function( aspect )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.SetAspect( aspect );
            }
            logger.info( this.__module(), "SetAspect( " + aspect + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetAspect: exception: " + e );
        }
    };
    this.SetOutputResolution = function( resolution )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.SetOutputResolution( resolution );
            }
            logger.info( this.__module(), "SetOutputResolution( " + resolution + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetOutputResolution: exception: " + e );
        }
    };
    this.SetPreferredHDRes = function( resolution )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.SetPreferredHDRes( resolution );
            }
            logger.info( this.__module(), "SetPreferredHDRes( " + resolution + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetPreferredHDRes: exception: " + e );
        }
    };
}

function BrowserProxyClass()
{
    this.__module = function()
    {
        return "proxy." + this.constructor.name;
    };
    this.SetToolbarState = function( state )
    {
        try
        {
            if ( window.Browser )
            {
                window.Browser.SetToolbarState( state );
            }
            logger.info( this.__module(), "SetToolbarState( " + state + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetToolbarState: exception: " + e );
        }
    };
    this.FrameLoadResetsState = function( state )
    {
        try
        {
            if ( window.Browser )
            {
                window.Browser.FrameLoadResetsState( state );
            }
            logger.info( this.__module(), "FrameLoadResetsState( " + state + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "FrameLoadResetsState: exception: " + e );
        }
    };
    this.Lower = function()
    {
        try
        {
            if ( window.Browser )
            {
                window.Browser.Lower();
            }
            logger.info( this.__module(), "Lower()" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "Lower: exception: " + e );
        }
    };
    this.Raise = function()
    {
        try
        {
            if ( window.Browser )
            {
                window.Browser.Raise();
            }
            logger.info( this.__module(), "Raise()" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "Raise: exception: " + e );
        }
    };
    this.Action = function( action )
    {
        try
        {
            if ( window.Browser )
            {
                window.Browser.Action( action );
            }
            logger.info( this.__module(), "Action( " + action + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "Action: exception: " + e );
        }
    };
}

function AVMediaProxyClass()
{
    this.onEvent = null;
    this.Event   = 0;

    if ( window.AVMedia )
    {
        try
        {
            window.AVMedia.onEvent = function()
            {
                try
                {
                    this.Event = window.AVMedia.Event;
                    if ( this.onEvent )
                    {
                        this.onEvent();
                    }
                }
                catch ( e )
                {
                    logger.error( this.__module(), "onEvent: exception: " + e );
                }
            }
        }
        catch ( e )
        {
            logger.error( this.__module(), "exception: " + e );
        }
    }

    this.__module = function()
    {
        return "proxy." + this.constructor.name;
    };
    this.Kill = function()
    {
        try
        {
            if ( window.AVMedia )
            {
                window.AVMedia.Kill();
            }
            logger.info( this.__module(), "Kill()" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "Kill: exception: " + e );
        }
    };
    this.Play = function( url )
    {
        try
        {
            if ( window.AVMedia )
            {
                window.AVMedia.Play( url );
            }
            logger.info( this.__module(), "Play( " + url + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "Play: exception: " + e );
        }
    };
    this.Pause = function()
    {
        try
        {
            if ( window.AVMedia )
            {
                window.AVMedia.Pause();
            }
            logger.info( this.__module(), "Play()" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "Play: exception: " + e );
        }
    };
    this.Continue = function()
    {
        try
        {
            if ( window.AVMedia )
            {
                window.AVMedia.Continue();
            }
            logger.info( this.__module(), "Continue()" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "Continue: exception: " + e );
        }
    };
    this.GetMSecPosition = function()
    {
        retval = 0;
        try
        {
            if ( window.AVMedia )
            {
                retval = window.AVMedia.GetMSecPosition();
            }
//            logger.info( this.__module(), "GetMSecPosition() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetMSecPosition: exception: " + e );
        }
        return retval;
    };
    this.SetMSecPosition = function( pos )
    {
        retval = 0;
        try
        {
            if ( window.AVMedia )
            {
                retval = window.AVMedia.SetMSecPosition( pos );
            }
            logger.info( this.__module(), "SetMSecPosition( " + pos + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetMSecPosition: exception: " + e );
        }
        return retval;
    };
    this.SetSpeed = function( speed )
    {
        try
        {
            if ( window.AVMedia )
            {
                window.AVMedia.SetSpeed( speed );
            }
            logger.info( this.__module(), "SetSpeed( " + speed + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetSpeed: exception: " + e );
        }
    };
    this.GetCurrentSpeed = function()
    {
        retval = 0;
        try
        {
            if ( window.AVMedia )
            {
                retval = window.AVMedia.GetCurrentSpeed();
            }
            logger.info( this.__module(), "GetCurrentSpeed() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetCurrentSpeed: exception: " + e );
        }
        return retval;
    };
    this.SetAudioPID = function( pid )
    {
        try
        {
            if ( window.AVMedia )
            {
                window.AVMedia.SetAudioPID( pid );
            }
            logger.info( this.__module(), "SetAudioPID( " + pid + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetAudioPID: exception: " + e );
        }
    };
    this.SetPrimarySubtitleLanguage = function( lang, bb )
    {
        try
        {
            if ( window.AVMedia )
            {
                window.AVMedia.SetPrimarySubtitleLanguage( lang, bb );
            }
            logger.info( this.__module(), "SetPrimarySubtitleLanguage( " + lang + ", " + bb + " )" );
        }
        catch ( e )
        {
            logger.error( this.__module(), "SetPrimarySubtitleLanguage: exception: " + e );
        }
    };
}

function PVRProxyClass()
{
    this.__module = function()
    {
        return "proxy." + this.constructor.name;
    };
    this.GetPltInfo = function()
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.GetPltInfo();
            }
            logger.info( this.__module(), "GetPltInfo() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetPltInfo: exception: " + e );
        }
        return retval;
    };
    this.GetStorageInfo = function()
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.GetStorageInfo();
            }
            logger.debug( this.__module(), "GetStorageInfo() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetStorageInfo: exception: " + e );
        }
        return retval;
    };
    this.GetDeviceInfo = function()
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.GetDeviceInfo();
            }
            logger.info( this.__module(), "GetDeviceInfo() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetDeviceInfo: exception: " + e );
        }
        return retval;
    };
    this.GetDeviceStatus = function( deviceId )
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.GetDeviceStatus( deviceId );
            }
            logger.info( this.__module(), "GetDeviceStatus( " + deviceId + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetDeviceStatus: exception: " + e );
        }
        return retval;
    };
    this.GetAssetById = function( assetId )
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.GetAssetById( assetId );
            }
//            logger.info( this.__module(), "GetAssetById( " + assetId + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetAssetById: exception: " + e );
        }
        return retval;
    };
    this.GetAssetIdList = function()
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.GetAssetIdList();
            }
//            logger.info( this.__module(), "GetAssetIdList() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetAssetIdList: exception: " + e );
        }
        return retval;
    };
    this.GetScheduleList = function()
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.GetScheduleList();
            }
//            logger.info( this.__module(), "GetScheduleList() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "GetScheduleList: exception: " + e );
        }
        return retval;
    };
    this.DeleteAsset = function( aa )
    {
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.DeleteAsset( aa );
            }
            logger.info( this.__module(), "DeleteAsset( " + aa + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "DeleteAsset: exception: " + e );
        }
        return retval;
    };
    this.AddSchedule = function( aa, bb, ff, gg, dd )
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.AddSchedule( aa, bb, ff, gg, dd );
            }
            logger.info( this.__module(), "AddSchedule( " + aa + ", " + bb + ", " + ff + ", " + gg + ", " + dd + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "AddSchedule: exception: " + e );
        }
        return retval;
    };
    this.DeleteSchedule = function()
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.DeleteSchedule();
            }
            logger.info( this.__module(), "DeleteSchedule() = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "DeleteSchedule: exception: " + e );
        }
        return retval;
    };
    this.RequestDeviceReformat = function( aa )
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.RequestDeviceReformat( aa );
            }
            logger.info( this.__module(), "RequestDeviceReformat( " + aa + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "RequestDeviceReformat: exception: " + e );
        }
        return retval;
    };
    this.FormatDevice = function( aa )
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.FormatDevice( aa );
            }
            logger.info( this.__module(), "FormatDevice( " + aa + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "FormatDevice: exception: " + e );
        }
        return retval;
    };
    this.StopRecording = function( aa )
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.StopRecording( aa );
            }
            logger.info( this.__module(), "StopRecording( " + aa + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( this.__module(), "StopRecording: exception: " + e );
        }
        return retval;
    };
}

try
{
    ASTBProxy         = new ASTBProxyClass;
    PVRProxy          = new PVRProxyClass;
    AVMediaProxy      = new AVMediaProxyClass;
    BrowserProxy      = new BrowserProxyClass;
    VideoDisplayProxy = new VideoDisplayProxyClass;
}
catch ( e )
{
    logger.error( e );
}
