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
            logger.info( "ASTBProxyClass.DefaultKeys( " + keys + " )" );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.DefaultKeys: exception: " + e );
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
            logger.info( "ASTBProxyClass.WithChannels( " + channels + " )" );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.WithChannels: exception: " + e );
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
            logger.info( "ASTBProxyClass.SetMouseState( " + state + " )" );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.SetMouseState: exception: " + e );
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
            logger.info( "ASTBProxyClass.SetKeyFunction( " + key + ", " + func + " )" );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.SetKeyFunction: exception: " + e );
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
            logger.info( "ASTBProxyClass.GetConfig( " + key + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.GetConfig: exception: " + e );
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
            logger.info( "ASTBProxyClass.GetSystemModel() = " + retval );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.GetSystemModel: exception: " + e );
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
            logger.info( "ASTBProxyClass.GetSystemSubmodel() = " + retval );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.GetSystemSubmodel: exception: " + e );
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
            logger.info( "ASTBProxyClass.GetMacAddress() = " + retval );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.GetMacAddress: exception: " + e );
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
            logger.info( "ASTBProxyClass.GetPowerState() = " + retval );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.GetPowerState: exception: " + e );
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
            logger.info( "ASTBProxyClass.SetPowerState( " + state + " )" );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.SetPowerState: exception: " + e );
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
            logger.info( "ASTBProxyClass.Reboot()" );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.Reboot: exception: " + e );
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
            logger.info( "ASTBProxyClass.Upgrade( " + aa + ", " + bb + " )" );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.Upgrade: exception: " + e );
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
//            logger.info( "ASTBProxyClass.SetLEDState( " + led + ", " + state + " )" );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.SetLEDState: exception: " + e );
        }
    };
    this.DebugString = function( debug )
    {
        logger.info( debug );
    };
    this.ErrorString = function( error )
    {
        logger.error( error );
    };
    this.SetConfig = function( key, value, cc )
    {
        try
        {
            if ( window.ASTB )
            {
                window.ASTB.SetConfig( key, value, cc );
            }
            logger.info( "ASTBProxyClass.SetConfig( " + key + ", " + value + ", " + cc + " )" );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.SetConfig: exception: " + e );
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
            logger.info( "ASTBProxyClass.CommitConfig()" );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.CommitConfig: exception: " + e );
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
            logger.info( "ASTBProxyClass.GetIPAddress() = " + retval );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.GetIPAddress: exception: " + e );
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
            logger.info( "ASTBProxyClass.GetSystemManufacturer() = " + retval );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.GetSystemManufacturer: exception: " + e );
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
            logger.info( "ASTBProxyClass.GetHardwareVersion() = " + retval );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.GetHardwareVersion: exception: " + e );
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
            logger.info( "ASTBProxyClass.GetSoftwareVersion() = " + retval );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.GetSoftwareVersion: exception: " + e );
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
            logger.info( "ASTBProxyClass.GetSystemInfo() = " + retval );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.GetSystemInfo: exception: " + e );
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
            logger.info( "ASTBProxyClass.GetSerialNumber() = " + retval );
        }
        catch ( e )
        {
            logger.error( "ASTBProxyClass.GetSerialNumber: exception: " + e );
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
            logger.info( "VideoDisplayProxyClass.SetChromaKey( " + key + " )" );
        }
        catch ( e )
        {
            logger.error( "VideoDisplayProxyClass.SetChromaKey: exception: " + e );
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
            logger.info( "VideoDisplayProxyClass.SetAlphaLevel( " + level + " )" );
        }
        catch ( e )
        {
            logger.error( "VideoDisplayProxyClass.SetAlphaLevel: exception: " + e );
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
            logger.info( "VideoDisplayProxyClass.RetainMouseState( " + state + " )" );
        }
        catch ( e )
        {
            logger.error( "VideoDisplayProxyClass.RetainMouseState: exception: " + e );
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
            logger.info( "VideoDisplayProxyClass.RetainAlphaLevel( " + level + " )" );
        }
        catch ( e )
        {
            logger.error( "VideoDisplayProxyClass.RetainAlphaLevel: exception: " + e );
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
            logger.info( "VideoDisplayProxyClass.SetAVAspectSwitching( " + switching + " )" );
        }
        catch ( e )
        {
            logger.error( "VideoDisplayProxyClass.SetAVAspectSwitching: exception: " + e );
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
            logger.info( "VideoDisplayProxyClass.SetAVAspect( " + aspect + " )" );
        }
        catch ( e )
        {
            logger.error( "VideoDisplayProxyClass.SetAVAspect: exception: " + e );
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
            logger.info( "VideoDisplayProxyClass.SetSubtitles( " + aa + ", " + bb + " )" );
        }
        catch ( e )
        {
            logger.error( "VideoDisplayProxyClass.SetSubtitles: exception: " + e );
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
            logger.info( "VideoDisplayProxyClass.SetTeletextFullscreen( " + fullscreen + " )" );
        }
        catch ( e )
        {
            logger.error( "VideoDisplayProxyClass.SetTeletextFullscreen: exception: " + e );
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
            logger.info( "VideoDisplayProxyClass.SetOutputFmt( " + format + " )" );
        }
        catch ( e )
        {
            logger.error( "VideoDisplayProxyClass.SetOutputFmt: exception: " + e );
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
            logger.info( "VideoDisplayProxyClass.SetAspect( " + aspect + " )" );
        }
        catch ( e )
        {
            logger.error( "VideoDisplayProxyClass.SetAspect: exception: " + e );
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
            logger.info( "VideoDisplayProxyClass.SetOutputResolution( " + resolution + " )" );
        }
        catch ( e )
        {
            logger.error( "VideoDisplayProxyClass.SetOutputResolution: exception: " + e );
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
            logger.info( "VideoDisplayProxyClass.SetPreferredHDRes( " + resolution + " )" );
        }
        catch ( e )
        {
            logger.error( "VideoDisplayProxyClass.SetPreferredHDRes: exception: " + e );
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
            logger.info( "BrowserProxyClass.SetToolbarState( " + state + " )" );
        }
        catch ( e )
        {
            logger.error( "BrowserProxyClass.SetToolbarState: exception: " + e );
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
            logger.info( "BrowserProxyClass.FrameLoadResetsState( " + state + " )" );
        }
        catch ( e )
        {
            logger.error( "BrowserProxyClass.FrameLoadResetsState: exception: " + e );
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
            logger.info( "BrowserProxyClass.Lower()" );
        }
        catch ( e )
        {
            logger.error( "BrowserProxyClass.Lower: exception: " + e );
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
            logger.info( "BrowserProxyClass.Raise()" );
        }
        catch ( e )
        {
            logger.error( "BrowserProxyClass.Raise: exception: " + e );
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
            logger.info( "BrowserProxyClass.Action( " + action + " )" );
        }
        catch ( e )
        {
            logger.error( "BrowserProxyClass.Action: exception: " + e );
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
                    logger.error( "AVMediaProxyClass.onEvent: exception: " + e );
                }
            }
        }
        catch ( e )
        {
            logger.error( "AVMediaProxyClass: exception: " + e );
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
            logger.info( "AVMediaProxyClass.Kill()" );
        }
        catch ( e )
        {
            logger.error( "AVMediaProxyClass.Kill: exception: " + e );
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
            logger.info( "AVMediaProxyClass.Play( " + url + " )" );
        }
        catch ( e )
        {
            logger.error( "AVMediaProxyClass.Play: exception: " + e );
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
            logger.info( "AVMediaProxyClass.Play()" );
        }
        catch ( e )
        {
            logger.error( "AVMediaProxyClass.Play: exception: " + e );
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
            logger.info( "AVMediaProxyClass.Continue()" );
        }
        catch ( e )
        {
            logger.error( "AVMediaProxyClass.Continue: exception: " + e );
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
//            logger.info( "AVMediaProxyClass.GetMSecPosition() = " + retval );
        }
        catch ( e )
        {
            logger.error( "AVMediaProxyClass.GetMSecPosition: exception: " + e );
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
            logger.info( "AVMediaProxyClass.SetMSecPosition( " + pos + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( "AVMediaProxyClass.SetMSecPosition: exception: " + e );
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
            logger.info( "AVMediaProxyClass.SetSpeed( " + speed + " )" );
        }
        catch ( e )
        {
            logger.error( "AVMediaProxyClass.SetSpeed: exception: " + e );
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
            logger.info( "AVMediaProxyClass.GetCurrentSpeed() = " + retval );
        }
        catch ( e )
        {
            logger.error( "AVMediaProxyClass.GetCurrentSpeed: exception: " + e );
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
            logger.info( "AVMediaProxyClass.SetAudioPID( " + pid + " )" );
        }
        catch ( e )
        {
            logger.error( "AVMediaProxyClass.SetAudioPID: exception: " + e );
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
            logger.info( "AVMediaProxyClass.SetPrimarySubtitleLanguage( " + lang + ", " + bb + " )" );
        }
        catch ( e )
        {
            logger.error( "AVMediaProxyClass.SetPrimarySubtitleLanguage: exception: " + e );
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
            logger.info( "PVRProxyClass.GetPltInfo() = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.GetPltInfo: exception: " + e );
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
            logger.info( "PVRProxyClass.GetStorageInfo() = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.GetStorageInfo: exception: " + e );
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
            logger.info( "PVRProxyClass.GetDeviceInfo() = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.GetDeviceInfo: exception: " + e );
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
            logger.info( "PVRProxyClass.GetDeviceStatus( " + deviceId + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.GetDeviceStatus: exception: " + e );
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
//            logger.info( "PVRProxyClass.GetAssetById( " + assetId + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.GetAssetById: exception: " + e );
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
//            logger.info( "PVRProxyClass.GetAssetIdList() = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.GetAssetIdList: exception: " + e );
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
//            logger.info( "PVRProxyClass.GetScheduleList() = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.GetScheduleList: exception: " + e );
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
            logger.info( "PVRProxyClass.DeleteAsset( " + aa + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.DeleteAsset: exception: " + e );
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
            logger.info( "PVRProxyClass.AddSchedule( " + aa + ", " + bb + ", " + ff + ", " + gg + ", " + dd + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.AddSchedule: exception: " + e );
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
            logger.info( "PVRProxyClass.DeleteSchedule() = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.DeleteSchedule: exception: " + e );
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
            logger.info( "PVRProxyClass.RequestDeviceReformat( " + aa + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.RequestDeviceReformat: exception: " + e );
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
            logger.info( "PVRProxyClass.FormatDevice( " + aa + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.FormatDevice: exception: " + e );
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
            logger.info( "PVRProxyClass.StopRecording( " + aa + " ) = " + retval );
        }
        catch ( e )
        {
            logger.error( "PVRProxyClass.StopRecording: exception: " + e );
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
