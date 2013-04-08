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

var _remoteServiceClassInst = null;
var _loggerClassInst        = null;

function LoggerClass()
{
    this.DEBUG    = 0;
    this.INFO     = 1;
    this.WARNING  = 2;
    this.ERROR    = 3;
    this.CRITICAL = 4;

    this.SEND_DEBUG_LOG_INTERVAL  = 5000;
    this.SEND_DEBUG_LOG_LIMIT     = 10;
    this.ONSCREEN_DEBUG_LOG_LIMIT = 20;

    this.debugLog         = [];
    this.debugDiv         = null;
    this.remoteDebug      = false;
    this.removeLogTimeout = null;
    this.remoteLogRequest = null;

    this.init = function()
    {
        try
        {
            this.debugDiv = document.createElement( 'div' );
            this.debugDiv.setAttribute( 'id', 'debugLog' );

            this.debugDiv.style.width      = 710;
            this.debugDiv.style.height     = 350;
            this.debugDiv.style.position   = "absolute";
            this.debugDiv.style.left       = 5;
            this.debugDiv.style.top        = 5;
            this.debugDiv.style.background = "#00000C";
            this.debugDiv.style.border     = "1px solid #000000";
            this.debugDiv.style.fontSize   = "12px";
            this.debugDiv.style.display    = "none";
            this.debugDiv.style.opacity    = 0.8;

            document.body.appendChild( this.debugDiv );
        }
        catch ( e )
        {
            stbApi.DebugFunction( "LoggerClass.init: exception: " + e );
        }
    };

    this.debug = function( text )
    {
        this._print( this.DEBUG, text );
    };

    this.info = function( text )
    {
        this._print( this.INFO, text );
    };

    this.warning = function( text )
    {
        this._print( this.WARNING, text );
    };

    this.error = function( text )
    {
        this._print( this.ERROR, text );
    };

    this.critical = function( text )
    {
        this._print( this.CRITICAL, text );
    };

    this.enableRemoteDebug = function( enable )
    {
        this.remoteDebug = enable;

        if ( enable )
        {
            if ( (this.debugDiv != null) && (this.debugDiv !== undefined) )
            {
                if ( this.debugDiv.style.display == "block" )
                {
                    this.info( "Disable Debug Logging." );
                    this.debugDiv.style.display = "none";
                }
            }

            _loggerClassInst = this;
            this.remoteLogTimeout = window.setTimeout( function()
            {
                _loggerClassInst._sendDebugLog();
            }, this.SEND_DEBUG_LOG_INTERVAL );
        }
        else
        {
            if ( this.remoteLogTimeout )
            {
                window.clearTimeout( this.remoteLogTimeout );
            }
        }
    };

    this._print = function( level, text )
    {
        try
        {
            if ( this.remoteDebug )
            {
                if ( this.debugLog.length > this.SEND_DEBUG_LOG_LIMIT )
                {
                    if ( this.remoteLogTimeout )
                    {
                        window.clearTimeout( this.remoteLogTimeout );
                    }
                    this._sendDebugLog();
                }
            }
            else
            {
                if ( this.debugLog.length >= this.ONSCREEN_DEBUG_LOG_LIMIT )
                {
                    this.debugLog.splice( 0, this.debugLog.length - (this.ONSCREEN_DEBUG_LOG_LIMIT - 1) );
                }
            }

            var logItem = {
                              timestamp: (new Date).getTime(),
                              level:     level,
                              log_text:  text
                          };

            this.debugLog.push( logItem );

            if ( !this.remoteDebug )
            {
                html = "";

                for ( i = 0; i < this.debugLog.length; i++ )
                {
                    html += "[" + this.debugLog[i].level + "] " + this.debugLog[i].timestamp + ": " + this.debugLog[i].log_text + "<br\>";
                }

                if ( document.getElementById( 'debugLog' ) != null )
                {
                    document.getElementById( 'debugLog' ).innerHTML = html;
                }
            }
        }
        catch ( e )
        {
//            if ( window.console )
//            {
//                window.console.log( "LoggerClass._print: exception: " + e );
//                window.console.log( "[" + level + "] " + (new Date).getTime() + ": " + text )
//            }
            stbApi.debugFunction( "LoggerClass._print: exception: " + e );
            stbApi.debugFunction( "[" + level + "] " + (new Date).getTime() + ": " + text );
        }
    };

    this._sendDebugLog = function()
    {
        if ( this.remoteDebug )
        {
            try
            {
                if ( this.debugLog.length > 0 )
                {
                    debugLogText = "[";
                    for ( i = 0; i < this.debugLog.length; i++ )
                    {
                        if ( i > 0 )
                        {
                            debugLogText += ",";
                        }
                        debugLogText += "{\"timestamp\":" + this.debugLog[i].timestamp + ",\"level\":" + this.debugLog[i].level + ",\"log_text\":\"" + encodeURIComponent( this.debugLog[i].log_text ) + "\"}";
                    }
                    debugLogText += "]";
    
                    this.debugLog.splice( 0, this.debugLog.length );
    
                    _loggerClassInst = this;
                    this.remoteLogRequest = new XMLHttpRequest;
                    this.remoteLogRequest.onreadystatechange = function()
                    {
                        if ( (this.readyState == 4) && (this.status == 200) )
                        {
                            remoteLogTimeout = window.setTimeout( function()
                            {
                                _loggerClassInst._sendDebugLog();
                            }, this.SEND_DEBUG_LOG_INTERVAL );
                        }
                    };
                    this.remoteLogRequest.open( "POST", "/aminopvr/api/stb/postLog", true );
                    this.remoteLogRequest.setRequestHeader( "Content-Type", "application/x-www-form-urlencoded" );
                    this.remoteLogRequest.send( "logData=" + encodeURIComponent( debugLogText ) );
                }
                else
                {
                    _loggerClassInst = this;
                    window.setTimeout( function()
                    {
                        _loggerClassInst._sendDebugLog();
                    }, this.SEND_DEBUG_LOG_INTERVAL );
                }
            }
            catch ( e )
            {
                stbApi.debugFunction( "LoggerClass._sendDebugLog: exception: " + e );
            }
        }
    };
}

function RemoteServiceClass()
{
    this.POLL_SHORT_INTERVAL = 100;
    this.POLL_LONG_INTERVAL  = 5000;

    this.pollServiceActive = false;

    this.pollRequest = null;
    this.statusRequest = null;
    this.channelRequest = null;

    this.init = function()
    {
        try
        {
            _remoteServiceClassInst = this;
            window.addEventListener( "load", function()
            {
                _remoteServiceClassInst._onLoad();
            }, false );

            logger.enableRemoteDebug( true );
        }
        catch ( e )
        {
            logger.critical( "RemoteServiceClass.Init: exception: " + e );
        }
    };

    this.powerOn = function()
    {
        try
        {
            _remoteServiceClassInst = this;
            window.addEventListener( "keypress", function( key )
            {
                _remoteServiceClassInst._keyListener( key );
            }, false );
            window.removeEventListener( "keypress", stbApi.keyEventFunctionPtr(), false );
        }
        catch ( e )
        {
            logger.critical( "RemoteServiceClass.PowerOn: exception: " + e );
        }
    };

    this._onLoad = function()
    {
        logger.init();

        _remoteServiceClassInst = this;
        window.setTimeout( function()
        {
            _remoteServiceClassInst._poll();
        }, _remoteServiceClassInst.POLL_SHORT_INTERVAL );
    };

    this._poll = function()
    {
        if ( !this.pollServerActive )
        {
            logger.warning( "RemoteServiceClass.Poll: Starting polling service" );
            this.pollServerActive = true;

            try
            {
                _remoteServiceClassInst = this;
                this.pollRequest = new XMLHttpRequest();
                this.pollRequest.open( "GET", "/aminopvr/api/stb/poll?init", true );
                this.pollRequest.onreadystatechange = this._pollStateChange;
                this.pollRequest.send();
            }
            catch ( e )
            {
                this.pollRequest = false;
                logger.critical( "RemoteServiceClass.Poll: exception: " + e );
            }
        }
        else
        {
            try
            {
                _remoteServiceClassInst = this;
                this.pollRequest = new XMLHttpRequest();
                this.pollRequest.open( "GET", "/aminopvr/api/stb/poll", true );
                this.pollRequest.onreadystatechange = this._pollStateChange;
                this.pollRequest.send();
            }
            catch ( e )
            {
                this.pollRequest = false;
                logger.critical( "RemoteServiceClass.Poll: exception: " + e );
            }
        }
    };

    this._pollStateChange = function()
    {
        if ( _remoteServiceClassInst.pollRequest.readyState == 4 )
        {
            try
            {
                if ( _remoteServiceClassInst.pollRequest.responseText.length > 0 )
                {
                    var responseItem = eval( '(' + _remoteServiceClassInst.pollRequest.responseText + ')' );
                    if ( responseItem['status'] == 'success' )
                    {
                    	if ( responseItem['data']['type'] == 'command' )
                    	{
                        	if ( responseItem['data']['command'] == 'show_osd' )
                        	{
                            	logger.info( "RemoteServiceClass._pollStateChange: command: show_osd." );
//                                stbApi.setChannelInstance().$(5000);
	                        }
    	                    else if ( responseItem['data']['command'] == 'play_stream' )
        	                {
            	                logger.warning( "RemoteServiceClass._pollStateChange: command: play_stream: url=" + responseItem['data']['url'] );

                	            stbApi.playStreamAction1( stbApi.setChannelInstance() );
                    	        b = new stbApi.playStreamClass( responseItem['data']['url'], "", true );
                        	    stbApi.playStreamAction2( b );
	                        }
    	                    else if ( responseItem['data']['command'] == 'get_channel_list' )
        	                {
            	                window.setTimeout( function()
                	            {
                    	            _remoteServiceClassInst._sendChannelList();
                        	    }, 5000 );
	                        }
    	                    else if ( responseItem['data']['command'] == 'remote_debug' )
        	                {
            	                if ( !logger.remoteDebug )
                	            {
                    	            logger.enableRemoteDebug( true );
                        	    }
	                            else
    	                        {
        	                        logger.enableRemoteDebug( false );
            	                }
                	        }
                    	    // else if ( responseItem['data']['command'] == 'debug' )
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
                    	        logger.warning( "RemoteServiceClass._pollStateChange: other command: " + responseItem['command'] );
                        	}
	                    }
    	                else if ( responseItem['data']['type'] == 'channel' )
        	            {
            	            stbApi.setChannelFunction( responseItem['channel'], 0 );
                	    }
                    	else if ( responseItem['data']['type'] == 'key' )
	                    {
    	                    evt          = new API_KeyboardEvent;
        	                evt.keyCode  = responseItem['data']['key'];
            	            logger.info( "RemoteServiceClass._pollStateChange: key: " + responseItem['data']['key'] );
                	        _remoteServiceClassInst._keyListener( evt );
                    	}
	                    else if ( responseItem['data']['type'] == 'unknown_message' )
    	                {
        	                logger.warning( "RemoteServiceClass._pollStateChange: unknown message received." );
            	        }
                	    else if ( responseItem['data']['type'] == 'timeout' )
                    	{
//                      	  logger.debug( "RemoteServiceClass._pollStateChange: timeout." );
	                    }
    	                else
        	            {
//          	              logger.warning( "RemoteServiceClass._pollStateChange: " + responseItem );
                	    }
                	}
                }

                window.setTimeout( function()
                {
                    _remoteServiceClassInst._poll();
                }, _remoteServiceClassInst.POLL_SHORT_INTERVAL );
            }
            catch ( e )
            {
                logger.error( "RemoteServiceClass._pollStateChange: exception: " + e + ", responseText: " + _remoteServiceClassInst.pollRequest.responseText );
                window.setTimeout( function()
                {
                    _remoteServiceClassInst._poll();
                } , _remoteServiceClassInst.POLL_LONG_INTERVAL );
            }

            _remoteServiceClassInst.pollRequest = false;
        }
    };

    this.setActiveChannel = function( channel )
    {
        try
        {
            logger.info( "RemoteServiceClass.setActiveChannel: " + channel );

            this.statusRequest = new XMLHttpRequest();
            this.statusRequest.onreadystatechange = function()
            {
                if ( (this.readyState == 4) && (this.status == 200) )
                {
                    logger.info( "RemoteServiceClass.setActiveChannel.onreadystatechange: done: " + this.responseText );
                }
            };
            this.statusRequest.open( "GET", "/aminopvr/api/stb/setActiveChannel?channel=" + channel, true );
            this.statusRequest.send();
        }
        catch ( e )
        {
            this.statusRequest = false;
            logger.error( "RemoteServiceClass.setActiveChannel: exception: " + e );
        }
    };

    this._sendChannelList = function()
    {
        try
        {
            channels = []
            for ( var i = 0; i < stbApi.channelList().length; i++ )
            {
                if ( stbApi.channelList()[i] != null )
                {
                    var channel = new API_ChannelClass();
                    channel.getChannel( stbApi.channelList()[i] );
                    channelStreams = []
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

            logger.debug( "RemoteServiceClass._sendChannelList" );

            this.channelRequest = new XMLHttpRequest();
            this.channelRequest.onreadystatechange = function()
            {
                if ( (this.readyState == 4) && (this.status == 200) )
                {
                    logger.info( "RemoteServiceClass._sendChannelList.onreadystatechange: done: " + this.responseText );
                }
            };
            this.channelRequest.open( "POST", "/aminopvr/api/stb/setChannelList", true );
            this.channelRequest.setRequestHeader( "Content-type", "application/x-www-form-urlencoded" );
            this.channelRequest.send( "channelList=" + encodeURIComponent( channelList ) );
        }
        catch ( e )
        {
            this.channelRequest = false;
            logger.error( "RemoteServiceClass._sendChannelList: exception: " + e );
        }
    };

    this._keyListener = function( b )
    {
        key = b.keyCode || b.charCode;
        logger.info( "RemoteServiceClass.KeyListener: key=" + key );

        try
        {
            stbApi.keyEventFunction( b );
        }
        catch ( e )
        {
            logger.error( "RemoteServiceClass.KeyListener: exception: " + e );
        }
    };

}

var stbApi        = new APIClass();
var logger        = new LoggerClass();
var remoteService = new RemoteServiceClass();
remoteService.init();

function PowerOn()
{
    if ( remoteService != null )
    {
        remoteService.powerOn();
    }
}
function SetActiveChannel( channel )
{
    if ( remoteService != null )
    {
        remoteService.setActiveChannel( channel );
    }
}
function DebugLog( log_text )
{
    if ( logger != null )
    {
        logger.info( log_text );
    }
}

/**
 * Converts the given data structure to a JSON string.
 * Argument: arr - The data structure that must be converted to JSON
 * Example: var json_string = array2json(['e', {pluribus: 'unum'}]);
 * 			var json = array2json({"success":"Sweet","failure":false,"empty_array":[],"numbers":[1,2,3],"info":{"name":"Binny","site":"http:\/\/www.openjs.com\/"}});
 * http://www.openjs.com/scripts/data/json_encode.php
 */
function Array2JSON( arr )
{
    var parts   = [];
    var is_list = (Object.prototype.toString.apply( arr ) === '[object Array]');

    for ( var key in arr )
    {
    	var value = arr[key];
        if ( typeof value == "object" )
        {
            //Custom handling for arrays
            if ( is_list )
                parts.push( Array2JSON( value ) );  /* :RECURSION: */
            else
            {
//                parts[key] = Array2JSON( value );   /* :RECURSION: */
                var str = '"' + key + '":';
                str += Array2JSON( value );         /* :RECURSION: */
                parts.push( str );
            }
        }
        else
        {
            var str = "";
            if ( !is_list )
                str = '"' + key + '":';

            //Custom handling for multiple data types
            if ( typeof value == "number" )
                str += value;               //Numbers
            else if ( value === false )
                str += 'false';             //The booleans
            else if ( value === true )
                str += 'true';
            else
                str += '"' + value + '"';   //All other things
            // :TODO: Is there any more datatype we should be in the lookout for? (Functions?)

            parts.push( str );
        }
    }
    var json = parts.join( "," );
    
    if ( is_list )
        return '[' + json + ']';    //Return numerical JSON
    return '{' + json + '}';        //Return associative JSON
}
