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

var __module = "service."

function LoggerClass()
{
    this.DEBUG    = 0;
    this.INFO     = 1;
    this.WARNING  = 2;
    this.ERROR    = 3;
    this.CRITICAL = 4;

    this._SEND_DEBUG_LOG_INTERVAL  = 5000;
    this._SEND_DEBUG_LOG_LIMIT     = 10;
    this._ONSCREEN_DEBUG_LOG_LIMIT = 20;

    this._debugLog         = [];
    this._debugDiv         = null;
    this._remoteDebug      = false;
    this._removeLogTimeout = null;
    this._remoteLogRequest = null;

    this.__module = function()
    {
        return "service." + this.constructor.name;
    };
    this.init = function()
    {
        try
        {
            this._debugDiv = document.createElement( 'div' );
            this._debugDiv.setAttribute( 'id', 'debugLog' );

            this._debugDiv.style.width      = 710;
            this._debugDiv.style.height     = 350;
            this._debugDiv.style.position   = "absolute";
            this._debugDiv.style.left       = 5;
            this._debugDiv.style.top        = 5;
            this._debugDiv.style.background = "#00000C";
            this._debugDiv.style.border     = "1px solid #000000";
            this._debugDiv.style.fontSize   = "12px";
            this._debugDiv.style.display    = "none";
            this._debugDiv.style.opacity    = 0.8;

            document.body.appendChild( this._debugDiv );
        }
        catch ( e )
        {
            if ( window.console )
            {
                window.console.log( "LoggerClass.init: exception: " + e );
            }
        }
    };

    this.debug = function( module, text )
    {
        this._print( this.DEBUG, module, text );
    };

    this.info = function( module, text )
    {
        this._print( this.INFO, module, text );
    };

    this.warning = function( module, text )
    {
        this._print( this.WARNING, module, text );
    };

    this.error = function( module, text )
    {
        this._print( this.ERROR, module, text );
    };

    this.critical = function( module, text )
    {
        this._print( this.CRITICAL, module, text );
    };

    this.getRemoteDebugEnabled = function()
    {
        return this._remoteDebug;
    }

    this.enableRemoteDebug = function( enable )
    {
        this._remoteDebug = enable;

        if ( enable )
        {
            if ( (this._debugDiv != null) && (this._debugDiv !== undefined) )
            {
                if ( this._debugDiv.style.display == "block" )
                {
                    this.info( this.__module(), "Disable Debug Logging." );
                    this._debugDiv.style.display = "none";
                }
            }

            this._remoteLogTimeout = window.setTimeout( function()
            {
                logger._sendDebugLog();
            }, this._SEND_DEBUG_LOG_INTERVAL );
        }
        else
        {
            if ( this._remoteLogTimeout )
            {
                window.clearTimeout( this._remoteLogTimeout );
            }
        }
    };

    this._print = function( level, module, text )
    {
        try
        {
            if ( this._remoteDebug )
            {
                if ( this._debugLog.length > this._SEND_DEBUG_LOG_LIMIT )
                {
                    if ( this._remoteLogTimeout )
                    {
                        window.clearTimeout( this._remoteLogTimeout );
                    }
                    this._sendDebugLog();
                }
            }
            else
            {
                if ( this._debugLog.length >= this._ONSCREEN_DEBUG_LOG_LIMIT )
                {
                    this._debugLog.splice( 0, this._debugLog.length - (this._ONSCREEN_DEBUG_LOG_LIMIT - 1) );
                }
            }

            var logItem = {
                              timestamp: (new Date).getTime(),
                              level:     level,
                              module:    module,
                              log_text:  encodeURIComponent( text )
                          };

            this._debugLog.push( logItem );

            if ( !this._remoteDebug )
            {
                html = "";

                for ( i = 0; i < this._debugLog.length; i++ )
                {
                    html += "[" + this._debugLog[i].level + "] " + this._debugLog[i].timestamp + ": <" + this._debugLog[i].module + "> " + this._debugLog[i].log_text + "<br\>";
                }

                if ( (this._debugDiv != null) && (this._debugDiv !== undefined) )
                {
                    this._debugDiv.innerHTML = html;
                }
            }
        }
        catch ( e )
        {
           if ( window.console )
           {
               window.console.log( "LoggerClass._print: exception: " + e );
               window.console.log( "[" + level + "] " + (new Date).getTime() + ": <" + module + "> " + text )
           }
        }
    };

    this._sendDebugLog = function()
    {
        if ( this._remoteDebug )
        {
            try
            {
                if ( this._debugLog.length > 0 )
                {
                    // debugLogText = "[";
                    // for ( i = 0; i < this._debugLog.length; i++ )
                    // {
                        // if ( i > 0 )
                        // {
                            // debugLogText += ",";
                        // }
                        // debugLogText += "{\"timestamp\":" + this._debugLog[i].timestamp + ",\"level\":" + this._debugLog[i].level + ",\"log_text\":\"" + encodeURIComponent( this._debugLog[i].log_text ) + "\"}";
                    // }
                    // debugLogText += "]";

                    debugLogText = Array2JSON( this._debugLog );

                    this._debugLog.splice( 0, this._debugLog.length );

                    this._remoteLogRequest = new XMLHttpRequest;
                    this._remoteLogRequest.onreadystatechange = function()
                    {
                        if ( (this.readyState == 4) && (this.status == 200) )
                        {
                            logger._remoteLogTimeout = window.setTimeout( function()
                            {
                                logger._sendDebugLog();
                            }, logger._SEND_DEBUG_LOG_INTERVAL );
                        }
                    };
                    this._remoteLogRequest.open( "POST", "/aminopvr/api/stb/postLog", true );
                    this._remoteLogRequest.setRequestHeader( "Content-Type", "application/x-www-form-urlencoded" );
                    this._remoteLogRequest.send( "logData=" + encodeURIComponent( debugLogText ) );
                }
                else
                {
                    window.setTimeout( function()
                    {
                        logger._sendDebugLog();
                    }, logger._SEND_DEBUG_LOG_INTERVAL );
                }
            }
            catch ( e )
            {
                if ( window.console )
                {
                    window.console.log( "LoggerClass._sendDebugLog: exception: " + e );
                }
            }
        }
    };
}

function RemoteServiceClass()
{
    this._POLL_SHORT_INTERVAL = 100;
    this._POLL_LONG_INTERVAL  = 5000;

    this._pollServiceActive = false;

    this._pollRequest = null;
    this._statusRequest = null;
    this._channelRequest = null;

    this.__module = function()
    {
        return "service." + this.constructor.name;
    };
    this.init = function()
    {
        try
        {
            window.addEventListener( "load", function()
            {
                remoteService._onLoad();
            }, false );

            logger.enableRemoteDebug( true );
        }
        catch ( e )
        {
            logger.critical( this.__module(), "Init: exception: " + e );
        }
    };

    this.powerOn = function()
    {
        try
        {
            window.addEventListener( "keypress", function( key )
            {
                remoteService._keyListener( key );
            }, false );
            window.removeEventListener( "keypress", stbApi.keyEventFunctionPtr(), false );
        }
        catch ( e )
        {
            logger.critical( this.__module(), "PowerOn: exception: " + e );
        }
    };

    this._onLoad = function()
    {
        logger.init();

        window.setTimeout( function()
        {
            remoteService._poll();
        }, remoteService._POLL_SHORT_INTERVAL );
    };

    this._poll = function()
    {
        if ( !this._pollServerActive )
        {
            logger.warning( this.__module(), "Poll: Starting polling service" );
            this._pollServerActive = true;

            try
            {
                this._pollRequest = new XMLHttpRequest();
                this._pollRequest.open( "GET", "/aminopvr/api/stb/poll?init", true );
                this._pollRequest.onreadystatechange = this._pollStateChange;
                this._pollRequest.send();
            }
            catch ( e )
            {
                this._pollRequest = false;
                logger.critical( this.__module(), "Poll: exception: " + e );
            }
        }
        else
        {
            try
            {
                this._pollRequest = new XMLHttpRequest();
                this._pollRequest.open( "GET", "/aminopvr/api/stb/poll", true );
                this._pollRequest.onreadystatechange = this._pollStateChange;
                this._pollRequest.send();
            }
            catch ( e )
            {
                this._pollRequest = false;
                logger.critical( this.__module(), "Poll: exception: " + e );
            }
        }
    };

    this._pollStateChange = function()
    {
        if ( remoteService._pollRequest.readyState == 4 )
        {
            try
            {
                if ( remoteService._pollRequest.responseText.length > 0 )
                {
                    var responseItem = eval( '(' + remoteService._pollRequest.responseText + ')' );
                    if ( responseItem['status'] == 'success' )
                    {
                    	if ( responseItem['data']['type'] == 'command' )
                    	{
                        	if ( responseItem['data']['command'] == 'show_osd' )
                        	{
                            	logger.info( this.__module(), "_pollStateChange: command: show_osd." );
//                                stbApi.setChannelInstance().$(5000);
	                        }
    	                    else if ( responseItem['data']['command'] == 'play_stream' )
        	                {
            	                logger.warning( this.__module(), "_pollStateChange: command: play_stream: url=" + responseItem['data']['url'] );

                	            stbApi.playStreamAction1( stbApi.setChannelInstance() );
                    	        b = new stbApi.playStreamClass( responseItem['data']['url'], "", true );
                        	    stbApi.playStreamAction2( b );
	                        }
    	                    else if ( responseItem['data']['command'] == 'get_channel_list' )
        	                {
            	                window.setTimeout( function()
                	            {
                    	            remoteService._sendChannelList();
                        	    }, 5000 );
	                        }
    	                    else if ( responseItem['data']['command'] == 'remote_debug' )
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
                    	        logger.warning( this.__module(), "_pollStateChange: other command: " + responseItem['command'] );
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
            	            logger.info( this.__module(), "_pollStateChange: key: " + responseItem['data']['key'] );
                	        remoteService._keyListener( evt );
                    	}
	                    else if ( responseItem['data']['type'] == 'unknown_message' )
    	                {
        	                logger.warning( this.__module(), "_pollStateChange: unknown message received." );
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
                    remoteService._poll();
                }, removeService._POLL_SHORT_INTERVAL );
            }
            catch ( e )
            {
                logger.error( this.__module(), "_pollStateChange: exception: " + e + ", responseText: " + _remoteService._pollRequest.responseText );
                window.setTimeout( function()
                {
                    _remoteService._poll();
                } , _remoteService._POLL_LONG_INTERVAL );
            }

            _remoteService._pollRequest = false;
        }
    };

    this.setActiveChannel = function( channel )
    {
        try
        {
            logger.info( this.__module(), "setActiveChannel: " + channel );

            this._statusRequest = new XMLHttpRequest();
            this._statusRequest.onreadystatechange = function()
            {
                if ( (this.readyState == 4) && (this.status == 200) )
                {
                    logger.info( this.__module(), "setActiveChannel.onreadystatechange: done: " + this.responseText );
                }
            };
            this._statusRequest.open( "GET", "/aminopvr/api/stb/setActiveChannel?channel=" + channel, true );
            this._statusRequest.send();
        }
        catch ( e )
        {
            this._statusRequest = false;
            logger.error( this.__module(), "setActiveChannel: exception: " + e );
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

            logger.debug( this.__module(), "_sendChannelList" );

            this._channelRequest = new XMLHttpRequest();
            this._channelRequest.onreadystatechange = function()
            {
                if ( (this.readyState == 4) && (this.status == 200) )
                {
                    logger.info( this.__module(), "_sendChannelList.onreadystatechange: done: " + this.responseText );
                }
            };
            this._channelRequest.open( "POST", "/aminopvr/api/stb/setChannelList", true );
            this._channelRequest.setRequestHeader( "Content-type", "application/x-www-form-urlencoded" );
            this._channelRequest.send( "channelList=" + encodeURIComponent( channelList ) );
        }
        catch ( e )
        {
            this._channelRequest = false;
            logger.error( this.__module(), "_sendChannelList: exception: " + e );
        }
    };

    this._keyListener = function( b )
    {
        key = b.keyCode || b.charCode;
        logger.info( this.__module(), "_keyListener: key=" + key );

        try
        {
            stbApi.keyEventFunction( b );
        }
        catch ( e )
        {
            logger.error( this.__module(), "_keyListener: exception: " + e );
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
