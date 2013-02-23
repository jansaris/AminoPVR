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
    this.DefaultKeys = function( keys )
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.DefaultKeys( keys );
            }
            DebugLog( "ASTBProxyClass.DefaultKeys( " + keys + " )" );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.DefaultKeys: exception: " + e );
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
            DebugLog( "ASTBProxyClass.WithChannels( " + channels + " )" );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.WithChannels: exception: " + e );
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
            DebugLog( "ASTBProxyClass.SetMouseState( " + state + " )" );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.SetMouseState: exception: " + e );
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
            DebugLog( "ASTBProxyClass.SetKeyFunction( " + key + ", " + func + " )" );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.SetKeyFunction: exception: " + e );
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
            DebugLog( "ASTBProxyClass.GetConfig( " + key + " ) = " + retval );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.GetConfig: exception: " + e );
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
            DebugLog( "ASTBProxyClass.GetSystemModel() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.GetSystemModel: exception: " + e );
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
            DebugLog( "ASTBProxyClass.GetSystemSubmodel() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.GetSystemSubmodel: exception: " + e );
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
            DebugLog( "ASTBProxyClass.GetMacAddress() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.GetMacAddress: exception: " + e );
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
            DebugLog( "ASTBProxyClass.GetPowerState() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.GetPowerState: exception: " + e );
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
            DebugLog( "ASTBProxyClass.SetPowerState( " + state + " )" );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.SetPowerState: exception: " + e );
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
            DebugLog( "ASTBProxyClass.Reboot()" );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.Reboot: exception: " + e );
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
            DebugLog( "ASTBProxyClass.Upgrade( " + aa + ", " + bb + " )" );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.Upgrade: exception: " + e );
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
//            DebugLog( "ASTBProxyClass.SetLEDState( " + led + ", " + state + " )" );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.SetLEDState: exception: " + e );
        }
    };
    this.DebugString = function( debug )
    {
        DebugLog( debug );
    };
    this.ErrorString = function( error )
    {
        DebugLog( error );
    };
    this.SetConfig = function( key, value, cc )
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.SetConfig( key, value, cc );
            }
            DebugLog( "ASTBProxyClass.SetConfig( " + key + ", " + value + ", " + cc + " )" );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.SetConfig: exception: " + e );
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
            DebugLog( "ASTBProxyClass.CommitConfig()" );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.CommitConfig: exception: " + e );
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
            DebugLog( "ASTBProxyClass.GetIPAddress() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.GetIPAddress: exception: " + e );
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
            DebugLog( "ASTBProxyClass.GetSystemManufacturer() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.GetSystemManufacturer: exception: " + e );
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
            DebugLog( "ASTBProxyClass.GetHardwareVersion() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.GetHardwareVersion: exception: " + e );
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
            DebugLog( "ASTBProxyClass.GetSoftwareVersion() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.GetSoftwareVersion: exception: " + e );
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
            DebugLog( "ASTBProxyClass.GetSystemInfo() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.GetSystemInfo: exception: " + e );
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
            DebugLog( "ASTBProxyClass.GetSerialNumber() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "ASTBProxyClass.GetSerialNumber: exception: " + e );
        }
        return retval;
    };
}

function VideoDisplayProxyClass()
{
    this.SetChromaKey = function( key )
    {
        try
        {
            if ( window.VideoDisplay )
            {
                window.VideoDisplay.SetChromaKey( key );
            }
            DebugLog( "VideoDisplayProxyClass.SetChromaKey( " + key + " )" );
        }
        catch ( e )
        {
            DebugLog( "VideoDisplayProxyClass.SetChromaKey: exception: " + e );
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
            DebugLog( "VideoDisplayProxyClass.SetAlphaLevel( " + level + " )" );
        }
        catch ( e )
        {
            DebugLog( "VideoDisplayProxyClass.SetAlphaLevel: exception: " + e );
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
            DebugLog( "VideoDisplayProxyClass.RetainMouseState( " + state + " )" );
        }
        catch ( e )
        {
            DebugLog( "VideoDisplayProxyClass.RetainMouseState: exception: " + e );
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
            DebugLog( "VideoDisplayProxyClass.RetainAlphaLevel( " + level + " )" );
        }
        catch ( e )
        {
            DebugLog( "VideoDisplayProxyClass.RetainAlphaLevel: exception: " + e );
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
            DebugLog( "VideoDisplayProxyClass.SetAVAspectSwitching( " + switching + " )" );
        }
        catch ( e )
        {
            DebugLog( "VideoDisplayProxyClass.SetAVAspectSwitching: exception: " + e );
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
            DebugLog( "VideoDisplayProxyClass.SetAVAspect( " + aspect + " )" );
        }
        catch ( e )
        {
            DebugLog( "VideoDisplayProxyClass.SetAVAspect: exception: " + e );
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
            DebugLog( "VideoDisplayProxyClass.SetSubtitles( " + aa + ", " + bb + " )" );
        }
        catch ( e )
        {
            DebugLog( "VideoDisplayProxyClass.SetSubtitles: exception: " + e );
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
            DebugLog( "VideoDisplayProxyClass.SetTeletextFullscreen( " + fullscreen + " )" );
        }
        catch ( e )
        {
            DebugLog( "VideoDisplayProxyClass.SetTeletextFullscreen: exception: " + e );
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
            DebugLog( "VideoDisplayProxyClass.SetOutputFmt( " + format + " )" );
        }
        catch ( e )
        {
            DebugLog( "VideoDisplayProxyClass.SetOutputFmt: exception: " + e );
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
            DebugLog( "VideoDisplayProxyClass.SetAspect( " + aspect + " )" );
        }
        catch ( e )
        {
            DebugLog( "VideoDisplayProxyClass.SetAspect: exception: " + e );
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
            DebugLog( "VideoDisplayProxyClass.SetOutputResolution( " + resolution + " )" );
        }
        catch ( e )
        {
            DebugLog( "VideoDisplayProxyClass.SetOutputResolution: exception: " + e );
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
            DebugLog( "VideoDisplayProxyClass.SetPreferredHDRes( " + resolution + " )" );
        }
        catch ( e )
        {
            DebugLog( "VideoDisplayProxyClass.SetPreferredHDRes: exception: " + e );
        }
    };
}

function BrowserProxyClass()
{
    this.SetToolbarState = function( state )
    {
        try
        {
            if ( window.Browser )
            {
                window.Browser.SetToolbarState( state );
            }
            DebugLog( "BrowserProxyClass.SetToolbarState( " + state + " )" );
        }
        catch ( e )
        {
            DebugLog( "BrowserProxyClass.SetToolbarState: exception: " + e );
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
            DebugLog( "BrowserProxyClass.FrameLoadResetsState( " + state + " )" );
        }
        catch ( e )
        {
            DebugLog( "BrowserProxyClass.FrameLoadResetsState: exception: " + e );
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
            DebugLog( "BrowserProxyClass.Lower()" );
        }
        catch ( e )
        {
            DebugLog( "BrowserProxyClass.Lower: exception: " + e );
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
            DebugLog( "BrowserProxyClass.Raise()" );
        }
        catch ( e )
        {
            DebugLog( "BrowserProxyClass.Raise: exception: " + e );
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
            DebugLog( "BrowserProxyClass.Action( " + action + " )" );
        }
        catch ( e )
        {
            DebugLog( "BrowserProxyClass.Action: exception: " + e );
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
                    DebugLog( "AVMediaProxyClass.onEvent: exception: " + e );
                }
            }
        }
        catch ( e )
        {
            DebugLog( "AVMediaProxyClass: exception: " + e );
        }
    }

    this.Kill = function()
    {
        try
        {
            if ( window.AVMedia )
            {
                window.AVMedia.Kill();
            }
            DebugLog( "AVMediaProxyClass.Kill()" );
        }
        catch ( e )
        {
            DebugLog( "AVMediaProxyClass.Kill: exception: " + e );
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
            DebugLog( "AVMediaProxyClass.Play( " + url + " )" );
        }
        catch ( e )
        {
            DebugLog( "AVMediaProxyClass.Play: exception: " + e );
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
            DebugLog( "AVMediaProxyClass.Play()" );
        }
        catch ( e )
        {
            DebugLog( "AVMediaProxyClass.Play: exception: " + e );
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
            DebugLog( "AVMediaProxyClass.Continue()" );
        }
        catch ( e )
        {
            DebugLog( "AVMediaProxyClass.Continue: exception: " + e );
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
//            DebugLog( "AVMediaProxyClass.GetMSecPosition() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "AVMediaProxyClass.GetMSecPosition: exception: " + e );
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
            DebugLog( "AVMediaProxyClass.SetMSecPosition( " + pos + " ) = " + retval );
        }
        catch ( e )
        {
            DebugLog( "AVMediaProxyClass.SetMSecPosition: exception: " + e );
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
            DebugLog( "AVMediaProxyClass.SetSpeed( " + speed + " )" );
        }
        catch ( e )
        {
            DebugLog( "AVMediaProxyClass.SetSpeed: exception: " + e );
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
            DebugLog( "AVMediaProxyClass.GetCurrentSpeed() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "AVMediaProxyClass.GetCurrentSpeed: exception: " + e );
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
            DebugLog( "AVMediaProxyClass.SetAudioPID( " + pid + " )" );
        }
        catch ( e )
        {
            DebugLog( "AVMediaProxyClass.SetAudioPID: exception: " + e );
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
            DebugLog( "AVMediaProxyClass.SetPrimarySubtitleLanguage( " + lang + ", " + bb + " )" );
        }
        catch ( e )
        {
            DebugLog( "AVMediaProxyClass.SetPrimarySubtitleLanguage: exception: " + e );
        }
    };
}

function PVRProxyClass()
{
    this.GetPltInfo = function()
    {
        retval = "";
        try
        {
            if ( window.PVR )
            {
                retval = window.PVR.GetPltInfo();
            }
            DebugLog( "PVRProxyClass.GetPltInfo() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.GetPltInfo: exception: " + e );
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
            DebugLog( "PVRProxyClass.GetStorageInfo() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.GetStorageInfo: exception: " + e );
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
            DebugLog( "PVRProxyClass.GetDeviceInfo() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.GetDeviceInfo: exception: " + e );
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
            DebugLog( "PVRProxyClass.GetDeviceStatus( " + deviceId + " ) = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.GetDeviceStatus: exception: " + e );
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
//            DebugLog( "PVRProxyClass.GetAssetById( " + assetId + " ) = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.GetAssetById: exception: " + e );
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
//            DebugLog( "PVRProxyClass.GetAssetIdList() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.GetAssetIdList: exception: " + e );
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
//            DebugLog( "PVRProxyClass.GetScheduleList() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.GetScheduleList: exception: " + e );
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
            DebugLog( "PVRProxyClass.DeleteAsset( " + aa + " ) = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.DeleteAsset: exception: " + e );
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
            DebugLog( "PVRProxyClass.AddSchedule( " + aa + ", " + bb + ", " + ff + ", " + gg + ", " + dd + " ) = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.AddSchedule: exception: " + e );
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
            DebugLog( "PVRProxyClass.DeleteSchedule() = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.DeleteSchedule: exception: " + e );
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
            DebugLog( "PVRProxyClass.RequestDeviceReformat( " + aa + " ) = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.RequestDeviceReformat: exception: " + e );
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
            DebugLog( "PVRProxyClass.FormatDevice( " + aa + " ) = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.FormatDevice: exception: " + e );
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
            DebugLog( "PVRProxyClass.StopRecording( " + aa + " ) = " + retval );
        }
        catch ( e )
        {
            DebugLog( "PVRProxyClass.StopRecording: exception: " + e );
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
    DebugLog( e );
}
