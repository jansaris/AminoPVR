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

var __module = "aminopvr.";

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

    this._consoleLogging   = false;
    this._debugLog         = [];
    this._debugDiv         = null;
    this._remoteDebug      = false;
    this._removeLogTimeout = null;
    this._remoteLogRequest = null;

    this.__module = function()
    {
        return __module + this.constructor.name;
    };
    this.init = function( consoleLogging )
    {
        this._consoleLogging = consoleLogging || false;

        if ( !this._consoleLogging )
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
            if ( !this._consoleLogging )
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
            else
            {
                if ( window.console )
                {
                    window.console.log( "[" + level + "] " + (new Date).getTime() + ": <" + module + "> " + text )
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

function AminoPVRClass()
{
    this.__module = function()
    {
        return __module + this.constructor.name;
    };

    this.getRecordingList = function()
    {
        var context           = this;
        var recordings        = [];
        var recordingsRequest = new XMLHttpRequest();

        logger.info( this.__module(), "getRecordingList: Downloading recording list" );

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
                                recordings[i] = responseItem["data"][row];
                            }
                        }

                        logger.info( context.__module(), "getRecordingList: onreadystatechange: Downloaded recording list; count = " + recordings.length );
                    }
                    catch ( e )
                    {
                        logger.error( context.__module(), "getRecordingList: onreadystatechange: exception: " + e );
                    }
                }
            }
        };
        recordingsRequest.open( "GET", "/aminopvr/api/getRecordingList", false );
        recordingsRequest.send();

        return recordings;
    };
}

var logger = new LoggerClass();
logger.init( true );

var aminopvr = new AminoPVRClass();
