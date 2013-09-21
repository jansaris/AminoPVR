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

function StbController()
{
    this._controller = new AminoPVRController( CONTROLLER_TYPE_RENDERER, this );

    this.__module = function()
    {
        return "aminopvr." + this.constructor.name;
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
            logger.enableRemoteDebug( true );
        }
        catch ( e )
        {
            logger.critical( this.__module(), "init: exception: " + e );
        }
    };
    this._onLoad = function()
    {
        logger.init();

        var self = this;
        window.setTimeout( function()
        {
            if ( self._controller )
            {
                self._controller.init();
            }
        }, 100 );
    };
    this.powerOn = function()
    {
        try
        {
            var self = this;
            window.addEventListener( "keypress", function( key )
            {
                self._keyListener( key );
            }, false );
            window.removeEventListener( "keypress", stbApi.keyEventFunctionPtr(), false );
        }
        catch ( e )
        {
            logger.critical( this.__module(), "powerOn: exception: " + e );
        }
    };
    this._callback = function( data )
    {
        try
        {
            if ( data["type"] == "command" )
            {
                this._handleCommand( data["data"] );
            }
            else if ( data["type"] == "status" )
            {
                this._handleStatus( data["data"] );
            }
            else if ( data["type"] == "key" )
            {
                evt          = new API_KeyboardEvent;
                evt.keyCode  = data["data"];
                logger.info( this.__module(), "_callback: key: " + data["data"] );
                this._keyListener( evt );
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
        }
    };

    this._handleCommand = function( data )
    {
        logger.warning( this.__module(), "_handleCommand: command: " + data["command"] );
        try
        {
            if ( data["command"] == "showOsd" )
            {
//                stbApi.setChannelInstance().$(5000);
            }
            else if ( data["command"] == "playRecording" )
            {
                logger.warning( this.__module(), "_handleCommand: command: playRecording: recordingId=" + data['id'] );

                var host          = "/";
                var recording     = aminopvr.getRecordingById( data["id"] );
                var generalConfig = aminopvr.getGeneralConfig();
                if ( generalConfig != null )
                {
                    host = "rtsp://" + location.hostname + ":" + generalConfig.getRtspServerPort() + "/";
                }
                if ( recording )
                {
                    stbApi.playStreamAction1( stbApi.setChannelInstance() );
                    b = new stbApi.playStreamClass( host + recording.getFilename(), "", true );
                    stbApi.playStreamAction2( b );
                }
            }
            else if ( data["command"] == "playStream" )
            {
                logger.warning( this.__module(), "_handleCommand: command: playStream: url=" + data['url'] );
    
                stbApi.playStreamAction1( stbApi.setChannelInstance() );
                b = new stbApi.playStreamClass( data['url'], "", true );
                stbApi.playStreamAction2( b );
            }
            else if ( data["command"] == "setChannelList" )
            {
                var self = this;
                window.setTimeout( function()
                {
                    self._setChannelList();
                }, 5000 );
            }
            else if ( data["command"] == 'setChannel' )
            {
                stbApi.setChannelFunction( data["channel"], 0 );
            }
            else if ( data["command"] == "reload" )
            {
                location.reload();
            }
            else if ( data["command"] == "remoteDebug" )
            {
                if ( !logger.getRemoteDebugEnabled() )
                {
                    logger.enableRemoteDebug( true );
                }
                else
                {
                    logger.enableRemoteDebug( false );
                }
            }
            // else if ( data['command'] == 'debug' )
            // {
                // if ( logger.debugDiv !== undefined && logger.debugDiv != null )
                // {
                    // if ( logger.debugDiv.style.display == "none" )
                    // {
                        // logger.warning( "RemoteServiceClass._pollStateChange: Enable Debug Logging." );
                        // logger.debugDiv.style.display = "block";
                    // }
                    // else
                    // {
                        // logger.warning( "RemoteServiceClass._pollStateChange: Disable Debug Logging." );
                        // logger.debugDiv.style.display = "none";
                    // }
                // }
            // }
            else
            {
                logger.warning( this.__module(), "_handleCommand: other command: " + data["command"] );
            }
        }
        catch ( e )
        {
            logger.error( this.__module(), "_handleCommand: exception: " + e + ", data: " + data );
            throw e;
        }
    };
    this._handleStatus = function( data )
    {
    };

    this._keyListener = function( b )
    {
        key = b.keyCode || b.charCode;
        logger.info( this.__module(), "_keyListener: key=" + key );

        switch ( key )
        {
            case 44:   // '<'
                b = new API_KeyboardEvent;
                b.keyCode = 37;     // left
                break;
            case 46:   // '>'
                b = new API_KeyboardEvent;
                b.keyCode = 39;     // right
                break;
            case 97:   // 'a'
                b = new API_KeyboardEvent;
                b.keyCode = 38;     // up
                break;
            case 109:   // 'm'
                b = new API_KeyboardEvent;
                b.keyCode = 8516;   // down
                break;
            case 122:   // 'z'
                b = new API_KeyboardEvent;
                b.keyCode = 40;
                break;
            default:
                break;
        }

        try
        {
            stbApi.keyEventFunction( b );
        }
        catch ( e )
        {
            logger.error( this.__module(), "_keyListener: exception: " + e );
        }
    };

    this._setChannelList = function()
    {
        try
        {
            logger.warning( this.__module(), "_setChannelList" );
            channels = [];
            for ( var i = 0; i < stbApi.channelList().length; i++ )
            {
                if ( stbApi.channelList()[i] != null )
                {
                    var channel = new API_ChannelClass();
                    channel.getChannel( stbApi.channelList()[i] );
                    channelStreams = [];
                    if ( channel.URLHD != "" )
                    {
                        channelStreams.push( { url: channel.URLHD, is_hd: 1 } );
                    }
                    if ( channel.URL != "" )
                    {
                        channelStreams.push( { url: channel.URL, is_hd: 0 } );
                    }
                    channelObject = { id:         i,
                                      epg_id:     channel.EPGID2,
                                      name:       channel.NameLong,
                                      name_short: channel.NameShort,
                                      logo:       channel.Logo1,
                                      thumbnail:  channel.Logo2,
                                      radio:      channel.Radio,
                                      streams:    channelStreams };
                    channels.push( channelObject );
                }
            }
            channelList = Array2JSON( channels );

            logger.debug( this.__module(), "_setChannelList" );

            var self    = this;
            var request = new JsonAjaxRequest();
            request.setCallback( function( status, context, data )
            {
                if ( status )
                {
                    logger.info( self.__module(), "_setChannelList.callback: done: " + data );
                }
            } );
            request.setRequestHeader( "Content-type", "application/x-www-form-urlencoded" );
            request.setPostData( "channelList=" + encodeURIComponent( channelList ) );
            request.send( "POST", "/aminopvr/api/stb/setChannelList", true );
        }
        catch ( e )
        {
            logger.error( this.__module(), "_setChannelList: exception: " + e );
        }
    };
    this.setActiveChannel = function( channel )
    {
        try
        {
            logger.info( this.__module(), "setActiveChannel: " + channel );

            var self    = this;
            var request = new JsonAjaxRequest();
            request.setCallback( function( status, context, data )
            {
                if ( status )
                {
                    logger.info( self.__module(), "setActiveChannel.callback: done: " + data );
                }
            } );
            request.send( "GET", "/aminopvr/api/stb/setActiveChannel/" + channel, true );
        }
        catch ( e )
        {
            logger.error( this.__module(), "setActiveChannel: exception: " + e );
        }
    };

}

var stbApi        = new APIClass();
var stbController = new StbController();
stbController.init();

function PowerOn()
{
    if ( stbController != null )
    {
        stbController.powerOn();
    }
}
function SetActiveChannel( channel )
{
    if ( stbController != null )
    {
        stbController.setActiveChannel( channel );
    }
}
function DebugLog( log_text )
{
    if ( logger != null )
    {
        logger.info( log_text );
    }
}
