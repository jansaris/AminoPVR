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

function JsonAjaxRequest()
{
    this._request  = null;
    this._context  = null;
    this._callback = null;
    this._headers  = new Array();
    this._postData = null;

    this.__module = function()
    {
        return "aminopvr." + this.constructor.name;
    };

    this.setContext = function( context )
    {
        this._context = context;
    };
    this.setCallback = function( callback )
    {
        this._callback = callback;
    };
    this.setRequestHeader = function( key, value )
    {
        this._headers[key] = value;
    };
    this.setPostData = function( data )
    {
        this._postData = data;
    };
    this.send = function( method, path, async )
    {
        var self = this;

        async = async || false;

        this._request = new XMLHttpRequest();
        this._request.onreadystatechange = function() { self._onReadyStateChange() };
        this._request.open( method, path, async );
        if ( method == "POST" )
        {
            for ( var key in this._headers )
            {
                this._request.setRequestHeader( key, this._headers[key] );
            }
            this._request.send( this._postData );
        }
        else
        {
            this._request.send();
        }
    };
    this._onReadyStateChange = function()
    {
        if ( this._request.readyState == 4 )
        {
            if ( this._request.status == 200 )
            {
                try
                {
                    var responseItem = eval( '(' + this._request.responseText + ')' );
                    if ( responseItem["status"] == "success" && "data" in responseItem )
                    {
                        this._callback && this._callback( true, this._context, responseItem["data"] );
                    }
                    else
                    {
                        this._callback && this._callback( true, this._context, new Array() );
                    }
                }
                catch ( e )
                {
                    logger.error( this.__module(), "_onReadyStateChange: exception: " + e );
                    this._callback && this._callback( false, this._context );
                }
            }
            else
            {
                logger.error( this.__module(), "_onReadyStateChange: status=" + this._request.status );
                this._callback && this._callback( false, this._context );
            }
        }
    };
}

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

    this.__module = function()
    {
        return "aminopvr." + this.constructor.name;
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

                    var request = new JsonAjaxRequest();
                    request.setCallback( function( status, context, data )
                    {
                        if ( status )
                        {
                            logger._remoteLogTimeout = window.setTimeout( function()
                            {
                                logger._sendDebugLog();
                            }, logger._SEND_DEBUG_LOG_INTERVAL );
                        }
                    } );
                    request.setRequestHeader( "Content-Type", "application/x-www-form-urlencoded" );
                    request.setPostData( "logData=" + encodeURIComponent( debugLogText ) );
                    request.send( "POST", "/aminopvr/api/stb/postLog", true );
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

function AminoPVRChannel()
{
    this._id     = -1;
    this._number = -1;
    this._epgId  = "";
    this._name   = "";
    this._logo   = "";
    this._url    = "";

    this.__module = function()
    {
        return "aminopvr." + this.constructor.name;
    };

    this.fromJson = function ( json )
    {
        this._id     = ("id"        in json) ? json["id"]        : -1;
        this._number = ("number"    in json) ? json["number"]    : -1;
        this._epgId  = ("epg_id"    in json) ? json["epg_id"]    : "";
        this._name   = ("name"      in json) ? json["name"]      : "<Unknown>";
        this._logo   = ("logo_path" in json) ? json["logo_path"] : "";
        this._url    = ("url"       in json) ? json["url"]       : "";
    };

    this.getId = function()
    {
        return this._id;
    };
    this.getNumber = function()
    {
        return this._number;
    };
    this.getEpgId = function()
    {
        return this._epgId;
    };
    this.getName = function()
    {
        return this._name;
    };
    this.getLogo = function()
    {
        return this._logo;
    };
    this.getUrl = function()
    {
        return this._url;
    };
}

function AminoPVREpgProgram()
{
    this._id            = -1;
    this._epgId         = "";
    this._title         = "";
    this._subtitle      = "";
    this._description   = "";
    this._startTime     = null;
    this._endTime       = null;

    this.__module = function()
    {
        return "aminopvr." + this.constructor.name;
    };

    this.fromJson = function( json )
    {
        this._id            = ("id"           in json) ? json["id"]           : -1;
        this._epgId         = ("epg_id"       in json) ? json["epg_id"]       : "";
        this._title         = ("title"        in json) ? json["title"]        : "<Unkown>";
        this._subtitle      = ("subtitle"     in json) ? json["subtitle"]     : "";
        this._description   = ("description"  in json) ? json["description"]  : "";
        this._startTime     = new Date( ("start_time" in json) ? json["start_time"] * 1000 : 0 );
        this._endTime       = new Date( ("end_time"   in json) ? json["end_time"] * 1000   : 0 );
    };

    this.getId = function()
    {
        return this._id;
    };
    this.getEpgId = function()
    {
        return this._epgId;
    };
    this.getTitle = function()
    {
        return this._title;
    };
    this.getFullTitle = function()
    {
        var fullTitle = this._title;
        if ( this._subtitle != "" )
        {
            fullTitle += ": " + this._subtitle;
        }
        return fullTitle;
    };
    this.getSubtitle = function()
    {
        return this._subtitle;
    };
    this.getDescription = function()
    {
        return this._description;
    };
    this.getStartTime = function()
    {
        return this._startTime;
    };
    this.getEndTime = function()
    {
        return this._endTime;
    };
}

function AminoPVRRecording()
{
    this._id            = -1;
    this._title         = "";
    this._subtitle      = "";
    this._description   = "";
    this._startTime     = null;
    this._endTime       = null;
    this._url           = "";
    this._marker        = 0;
    this._channelId     = -1;
    this._channelName   = "";

    this.__module = function()
    {
        return "aminopvr." + this.constructor.name;
    };

    this.fromJson = function( json )
    {
        this._id            = ("id"           in json) ? json["id"]           : -1;
        this._title         = ("title"        in json) ? json["title"]        : "<Unkown>";
        this._subtitle      = ("subtitle"     in json) ? json["subtitle"]     : "";
        this._description   = ("description"  in json) ? json["description"]  : "";
        this._startTime     = new Date( ("start_time" in json) ? json["start_time"] * 1000 : 0 );
        this._endTime       = new Date( ("end_time"   in json) ? json["end_time"] * 1000   : 0 );
        this._url           = ("url"          in json) ? json["url"]          : "";
        this._marker        = ("marker"       in json) ? json["marker"]       : 0;
        this._channelId     = ("channel_id"   in json) ? json["channel_id"]   : -1;
        this._channelName   = ("channel_name" in json) ? json["channel_name"] : "<Unknown>";
    };

    this.getId = function()
    {
        return this._id;
    };
    this.getTitle = function()
    {
        return this._title;
    };
    this.getFullTitle = function()
    {
        var fullTitle = this._title;
        if ( this._subtitle != "" )
        {
            fullTitle += ": " + this._subtitle;
        }
        return fullTitle;
    };
    this.getSubtitle = function()
    {
        return this._subtitle;
    };
    this.getDescription = function()
    {
        return this._description;
    };
    this.getStartTime = function()
    {
        return this._startTime;
    };
    this.getEndTime = function()
    {
        return this._endTime;
    };
    this.getUrl = function()
    {
        return this._url;
    };
    this.getMarker = function()
    {
        return this._marker;
    };
    this.getChannelId = function()
    {
        return this._channelId;
    };
    this.getChannelName = function()
    {
        return this._channelName;
    };
}

function AminoPVRClass()
{
    this.__module = function()
    {
        return "aminopvr." + this.constructor.name;
    };

    this._formatArguments = function( arguments )
    {
        var argString = "";
        if ( arguments != {} )
        {
            for ( var key in arguments )
            {
                if ( argString == "" )
                {
                    argString += "?";
                }
                else
                {
                    argString += "&";
                }
                argString += key + "=" + arguments[key];
            }
        }
        return argString;
    }

    this.getChannelList = function( context, callback, async )
    {
        var requestContext         = {};
        requestContext["context"]  = context;
        requestContext["callback"] = callback;

        var self = this;

        logger.info( this.__module(), "getChannelList: Downloading channel list" );

        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, channels ) { self._channelListCallback( status, context, channels ) } );
        request.send( "GET", "/aminopvr/api/getChannelList", async );
    };

    this._channelListCallback = function( status, context, channels )
    {
        if ( status )
        {
            try
            {
                var pvrChannels = [];
                for ( var i in channels )
                {
                    pvrChannels[i] = new AminoPVRChannel();
                    pvrChannels[i].fromJson( channels[i] )
                }

                logger.info( this.__module(), "_channelListCallback: Downloaded channel list; count = " + pvrChannels.length );

                if ( "callback" in context )
                {
                    context["callback"]( true, context["context"], pvrChannels );
                }
            }
            catch ( e )
            {
                logger.error( this.__module(), "_channelListCallback: exception: " + e );
                if ( "callback" in context )
                {
                    context["callback"]( false, context["context"] );
                }
            }
        }
        else
        {
            logger.error( this.__module(), "_channelListCallback: Downloading channel list failed" );
            if ( "callback" in context )
            {
                context["callback"]( false, context["context"] );
            }
        }
    };

    this.getNowNextProgramList = function( context, callback, async )
    {
        var requestContext         = {};
        requestContext["context"]  = context;
        requestContext["callback"] = callback;

        logger.info( this.__module(), "getNowNextProgramList: Downloading now/next program list" );

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, programs ) { self._nowNextProgramListCallback( status, context, programs ) } );
        request.send( "GET", "/aminopvr/api/getNowNextProgramList", async );
    };
    this._nowNextProgramListCallback = function( status, context, programs )
    {
        if ( status )
        {
            try
            {
                var pvrPrograms = new Array();
                for ( var epgId in programs )
                {
                    pvrPrograms[epgId] = [];
                    for ( var i in programs[epgId] )
                    {
                        pvrPrograms[epgId][i] = new AminoPVREpgProgram();
                        pvrPrograms[epgId][i].fromJson( programs[epgId][i] )
                    }
                }

                logger.info( this.__module(), "_nowNextProgramListCallback: Downloaded now/next program list; count = " + pvrPrograms.length );

                if ( "callback" in context )
                {
                    context["callback"]( true, context["context"], pvrPrograms );
                }
            }
            catch ( e )
            {
                logger.error( this.__module(), "_nowNextProgramListCallback: exception: " + e );
                if ( "callback" in context )
                {
                    context["callback"]( false, context["context"] );
                }
            }
        }
        else
        {
            logger.error( this.__module(), "_nowNextProgramListCallback: Downloading now/next program list failed" );
            if ( "callback" in context )
            {
                context["callback"]( false, context["context"] );
            }
        }
    };

    this.getRecordingList = function( context, callback, async, offset, count )
    {
        var requestContext         = {};
        requestContext["context"]  = context;
        requestContext["callback"] = callback;

        logger.info( this.__module(), "getRecordingList: Downloading recording list" );

        var arguments = "";
        if ( offset != undefined )
        {
            arguments += "offset=" + offset + "&";
        }
        if ( count != undefined )
        {
            arguments += "count" + count;
        }
        if ( arguments != "" )
        {
            arguments = "?" + arguments;
        }

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, recordings ) { self._recordingListCallback( status, context, recordings ) } );
        request.send( "GET", "/aminopvr/api/getRecordingList" + arguments, async );
    };
    this._recordingListCallback = function( status, context, recordings )
    {
        if ( status )
        {
            try
            {
                var pvrRecordings = [];
                for ( var i in recordings )
                {
                    pvrRecordings[i] = new AminoPVRRecording();
                    pvrRecordings[i].fromJson( recordings[i] )
                }

                logger.info( this.__module(), "_recordingListCallback: Downloaded recordings list; count = " + pvrRecordings.length );

                if ( "callback" in context )
                {
                    context["callback"]( true, context["context"], pvrRecordings );
                }
            }
            catch ( e )
            {
                logger.error( this.__module(), "_recordingListCallback: exception: " + e );
                if ( "callback" in context )
                {
                    context["callback"]( false, context["context"] );
                }
            }
        }
        else
        {
            logger.error( this.__module(), "_recordingListCallback: Downloading recording list failed" );
            if ( "callback" in context )
            {
                context["callback"]( false, context["context"] );
            }
        }
    };
}

var logger   = new LoggerClass();
var aminopvr = new AminoPVRClass();
