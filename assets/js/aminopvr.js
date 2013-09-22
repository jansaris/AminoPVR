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

function JsonAjaxRequest()
{
    this._request  = null;
    this._context  = null;
    this._callback = null;
    this._headers  = new Array();
    this._postData = null;
    this._path     = "";

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

        this._path    = path;
        this._request = new XMLHttpRequest();
        this._request.onreadystatechange = function() { self._onReadyStateChange(); };
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
                    else if ( responseItem["status"] == "success" )
                    {
                        this._callback && this._callback( true, this._context, new Array() );
                    }
                    else
                    {
                        this._callback && this._callback( false, this._context, new Array() );
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
                logger.warning( this.__module(), "_onReadyStateChange: status=" + this._request.status + ", path=" + this._path );
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
    };

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
                    window.console.log( "[" + level + "] " + (new Date).getTime() + ": <" + module + "> " + text );
                }
            }
        }
        catch ( e )
        {
           if ( window.console )
           {
               window.console.log( "LoggerClass._print: exception: " + e );
               window.console.log( "[" + level + "] " + (new Date).getTime() + ": <" + module + "> " + text );
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
                    debugLogText = Array2JSON( this._debugLog );

                    this._debugLog.splice( 0, this._debugLog.length );

                    var request = new JsonAjaxRequest();
                    request.setCallback( function( status, context, data )
                    {
                        logger._remoteLogTimeout = window.setTimeout( function()
                        {
                            logger._sendDebugLog();
                        }, logger._SEND_DEBUG_LOG_INTERVAL );
                    } );
                    request.setRequestHeader( "Content-Type", "application/x-www-form-urlencoded" );
                    request.setPostData( "logData=" + encodeURIComponent( debugLogText ) );
                    request.send( "POST", "/api/postLog", true );
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

function AminoPVRGeneralConfig()
{
    this._recordingPath         = "";
    this._inputStreamSupport    = "";
    this._serverPort            = "";
    this._rtspServerPort        = "";
    this._provider              = "";
    this._apiKey                = "";
    this._localAccessNets       = "";
    this._timeslotDelta         = "";

    this.__module = function()
    {
        return "aminopvr." + this.constructor.name;
    };

    this.fromJson = function( json )
    {
        this._recordingPath         = ("recording_path"         in json) ? json["recording_path"]       : "";
        this._inputStreamSupport    = ("input_stream_support"   in json) ? json["input_stream_support"] : "";
        this._serverPort            = ("server_port"            in json) ? json["server_port"]          : "";
        this._rtspServerPort        = ("rtsp_server_port"       in json) ? json["rtsp_server_port"]     : "";
        this._provider              = ("provider"               in json) ? json["provider"]             : "";
        this._apiKey                = ("api_key"                in json) ? json["api_key"]              : "";
        this._localAccessNets       = ("local_access_nets"      in json) ? json["local_access_nets"]    : "";
        this._timeslotDelta         = ("timeslot_delta"         in json) ? json["timeslot_delta"]       : "";
    };
    this.getRecordingPath = function()
    {
        return this._recordingPath;
    };
    this.getInputStreamSupport = function()
    {
        return this._inputStreamSupport;
    };
    this.getServerPort = function()
    {
        return this._serverPort;
    };
    this.getRtspServerPort = function()
    {
        return this._rtspServerPort;
    };
    this.getProvider = function()
    {
        return this._provider;
    };
    this.getApiKey = function()
    {
        return this._apiKey;
    };
    this.getLocalAccessNets = function()
    {
        return this._localAccessNets;
    };
    this.getTimeslotDelta = function()
    {
        return this._timeslotDelta;
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
    this._id             = -1;
    this._epgId          = "";
    this._title          = "";
    this._subtitle       = "";
    this._description    = "";
    this._startTime      = null;
    this._endTime        = null;
    this._genres         = new Array();
    this._actors         = new Array();
    this._directors      = new Array();
    this._presenters     = new Array();
    this._ratings        = new Array();
    this._aspectRatio    = "";
    this._parentalRating = "";

    this.__module = function()
    {
        return "aminopvr." + this.constructor.name;
    };

    this.fromJson = function( json )
    {
        this._id             = ("id"              in json) ? json["id"]              : -1;
        this._epgId          = ("epg_id"          in json) ? json["epg_id"]          : "";
        this._title          = ("title"           in json) ? json["title"]           : "<Unkown>";
        this._subtitle       = ("subtitle"        in json) ? json["subtitle"]        : "";
        this._description    = ("description"     in json) ? json["description"]     : "";
        this._startTime      = new Date( ("start_time" in json) ? json["start_time"] * 1000 : 0 );
        this._endTime        = new Date( ("end_time"   in json) ? json["end_time"] * 1000   : 0 );
        this._genres         = ("genres"          in json) ? json["genres"]          : new Array();
        this._actors         = ("actors"          in json) ? json["actors"]          : new Array();
        this._directors      = ("directors"       in json) ? json["directors"]       : new Array();
        this._presenters     = ("presenters"      in json) ? json["presenters"]      : new Array();
        this._ratings        = ("ratings"         in json) ? json["ratings"]         : new Array();
        this._aspectRatio    = ("aspect_ratio"    in json) ? json["aspect_ratio"]    : "";
        this._parentalRating = ("parental_rating" in json) ? json["parental_rating"] : "";
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
    this.getGenres = function()
    {
        return this._genres;
    };
    this.getActors = function()
    {
        return this._actors;
    };
    this.getDirectors = function()
    {
        return this._directors;
    };
    this.getPresenters = function()
    {
        return this._presenters;
    };
    this.getRatings = function()
    {
        return this._ratings;
    };
    this.getAspectRatio = function()
    {
        return this._aspectRatio;
    };
    this.getParentalRating = function()
    {
        return this._parentalRating;
    };
}

function AminoPVRRecording()
{
    this._id            = -1;
    this._scheduleId    = -1;
    this._title         = "";
    this._startTime     = null;
    this._endTime       = null;
    this._url           = "";
    this._filename      = "";
    this._marker        = 0;
    this._channelId     = -1;
    this._channelName   = "";
    this._epgProgramId  = -1;
    this._epgProgram    = null;

    this.__module = function()
    {
        return "aminopvr." + this.constructor.name;
    };

    this.fromJson = function( json )
    {
        this._id            = ("id"             in json) ? json["id"]             : -1;
        this._scheduleId    = ("schedule_id"    in json) ? json["schedule_id"]    : -1;
        this._title         = ("title"          in json) ? json["title"]          : "<Unkown>";
        this._subtitle      = ("subtitle"       in json) ? json["subtitle"]       : "";
        this._description   = ("description"    in json) ? json["description"]    : "";
        this._startTime     = new Date( ("start_time" in json) ? json["start_time"] * 1000 : 0 );
        this._endTime       = new Date( ("end_time"   in json) ? json["end_time"] * 1000   : 0 );
        this._url           = ("url"            in json) ? json["url"]            : "";
        this._filename      = ("filename"       in json) ? json["filename"]       : "";
        this._marker        = ("marker"         in json) ? json["marker"]         : 0;
        this._channelId     = ("channel_id"     in json) ? json["channel_id"]     : -1;
        this._channelName   = ("channel_name"   in json) ? json["channel_name"]   : "<Unknown>";
        this._epgProgramId  = ("epg_program_id" in json) ? json["epg_program_id"] : -1;
        this._epgProgram    = ("epg_program"    in json) ? new AminoPVREpgProgram().fromJson( json["epg_program"] ) : null;
    };

    this.getId = function()
    {
        return this._id;
    };
    this.getScheduleId = function()
    {
        return this._scheduleId;
    };
    this.getTitle = function()
    {
        return this._title;
    };
    this.getFullTitle = function()
    {
        var fullTitle = this._title;
        if ( this.epgProgram )
        {
            fullTitle = this.epgProgram.getTitle();
            if ( this.epgProgram.getSubtitle() != "" )
            {
                fullTitle += ": " + this.epgProgram.getSubtitle();
            }
        }
        return fullTitle;
    };
    this.getSubtitle = function()
    {
        return (this.epgProgram ? this.epgProgram.getSubtitle() : "");
    };
    this.getDescription = function()
    {
        return (this.epgProgram ? this.epgProgram.getDescription() : "");
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
    this.getFilename = function()
    {
        return this._filename;
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
    this.getEpgProgramId = function()
    {
        return this._epgProgramId;
    };
    this.getEpgProgram = function()
    {
        return this._epgProgram;
    };
    this.readMarker = function( context, callback, async )
    {
        var requestContext         = {};
        requestContext["context"]  = context;
        requestContext["callback"] = callback;

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, data )
        {
            if ( status )
            {
                logger.info( self.__module(), "readMarker.callback: read marker data: marker=" + data["marker"] );

                self._marker = data["marker"];

                context["callback"]( true, context["context"], self._marker );
            }
            else
            {
                context["callback"]( false, context["context"] );
            }
        } );
        request.send( "GET", "/api/recordings/getRecordingMarker/" + this._id, async );
    };
    this.writeMeta = function( marker, context, callback, async )
    {
        logger.info( this.__module(), "writeMeta( " + marker + " )" );

        this._marker = marker;

        var requestContext         = {};
        requestContext["context"]  = context;
        requestContext["callback"] = callback;

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, data )
        {
            if ( status )
            {
                logger.info( self.__module(), "writeMeta.callback: saved marker data" );

                context["callback"]( true, context["context"], self._marker );
            }
            else
            {
                context["callback"]( false, context["context"] );
            }
        } );
        request.send( "GET", "/api/recordings/setRecordingMarker/" + this._id + "/" + this._marker, async );
    };
    this.deleteFromDb = function()
    {
        logger.info( this.__module(), "deleteFromDb()" );

        var requestContext         = {};
        requestContext["deleted"]  = false;

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, data )
        {
            if ( status )
            {
                logger.info( self.__module(), "deleteFromDb.callback: deleted recording" );

                context["deleted"] = true;
            }
        } );
        request.send( "GET", "/api/recordings/deleteRecording/" + this._id, false );

        return requestContext["deleted"];
    };
}

function AminoPVRSchedule()
{
    this.SCHEDULE_TYPE_ONCE                 = 1;
    this.SCHEDULE_TYPE_TIMESLOT_EVERY_DAY   = 2;
    this.SCHEDULE_TYPE_TIMESLOT_EVERY_WEEK  = 3;
    this.SCHEDULE_TYPE_ONCE_EVERY_DAY       = 4;
    this.SCHEDULE_TYPE_ONCE_EVERY_WEEK      = 5;
    this.SCHEDULE_TYPE_ANY_TIME             = 6;
    this.SCHEDULE_TYPE_MANUAL_EVERY_DAY     = 7;
    this.SCHEDULE_TYPE_MANUAL_EVERY_WEEKDAY = 8;
    this.SCHEDULE_TYPE_MANUAL_EVERY_WEEKEND = 9;
    this.SCHEDULE_TYPE_MANUAL_EVERY_WEEK    = 10;

    this.DUPLICATION_METHOD_NONE        = 0;
    this.DUPLICATION_METHOD_TITLE       = 1;
    this.DUPLICATION_METHOD_SUBTITLE    = 2;
    this.DUPLICATION_METHOD_DESCRIPTION = 4;

    this._id                = -1;
    this._type              = -1;
    this._channelId         = -1;
    this._startTime         = null;
    this._endTime           = null;
    this._title             = "";
    this._preferHd          = false;
    this._preferUnscrambled = false;
    this._dupMethod         = -1;
    this._startEarly        = 0;
    this._endLate           = 0;
    this._inactive          = false;

    this.__module = function()
    {
        return "aminopvr." + this.constructor.name;
    };

    this.fromJson = function( json )
    {
        this._id                = ("id"                     in json) ? json["id"]                   : -1;
        this._type              = ("type"                   in json) ? json["type"]                 : -1;
        this._channelId         = ("channel_id"             in json) ? json["channel_id"]           : -1;
        this._startTime         = new Date( ("start_time"   in json) ? json["start_time"] * 1000    : 0 );
        this._endTime           = new Date( ("end_time"     in json) ? json["end_time"] * 1000      : 0 );
        this._title             = ("title"                  in json) ? json["title"]                : "<Unkown>";
        this._preferHd          = ("prefer_hd"              in json) ? json["prefer_hd"]            : false;
        this._preferUnscrambled = ("prefer_unscrambled"     in json) ? json["prefer_unscrambled"]   : false;
        this._dupMethod         = ("dup_method"             in json) ? json["dup_method"]           : -1;
        this._startEarly        = ("start_early"            in json) ? json["start_early"]          : 0;
        this._endLate           = ("end_late"               in json) ? json["start_late"]           : 0;
        this._inactive          = ("inactive"               in json) ? json["inactive"]             : false;
    };
    this.toJson = function()
    {
        json = {
            "id":                   this._id,
            "type":                 this._type,
            "channel_id":           this._channelId,
            "start_time":           Math.round( this._startTime.getTime() / 1000 ),
            "end_time":             Math.round( this._endTime.getTime()   / 1000 ),
            "title":                this._title,
            "prefer_hd":            this._preferHd,
            "prefer_unscrambled":   this._preferUnscrambled,
            "dup_method":           this._dupMethod,
            "start_early":          this._startEarly,
            "end_late":             this._endLate,
            "inactive":             this._inactive
        };
        return json;
    };

    this.getId = function()
    {
        return this._id;
    };
    this.getType = function()
    {
        return this._type;
    };
    this.setType = function( type )
    {
        this._type = type;
    };
    this.getChannelId = function()
    {
        return this._channelId;
    };
    this.setChannelId = function( channelId )
    {
        this._channelId = channelId;
    };
    this.getStartTime = function()
    {
        return this._startTime;
    };
    this.setStartTime = function( startTime )
    {
        this._startTime = new Date( startTime * 1000 );
    };
    this.getEndTime = function()
    {
        return this._endTime;
    };
    this.setEndTime = function( endTime )
    {
        this._endTime = new Date( endTime * 1000 );
    };
    this.getTitle = function()
    {
        return this._title;
    };
    this.setTitle = function( title )
    {
        this._title = title;
    };
    this.getPreferHd = function()
    {
        return this._preferHd;
    };
    this.setPreferHd = function( preferHd )
    {
        this._preferHd = preferHd;
    };
    this.getPreferUnscrambled = function()
    {
        return this._preferUnscrambled;
    };
    this.setPreferUnscrambled = function( preferUnscrambled )
    {
        this._preferUnscrambled = preferUnscrambled;
    };
    this.getDupMethod = function()
    {
        return this._dupMethod;
    };
    this.setDupMethod = function( dupMethod )
    {
        this._dupMethod = dupMethod;
    };
    this.getStartEarly = function()
    {
        return this._startEarly;
    };
    this.setStartEarly = function( startEarly )
    {
        this._startEarly = startEarly;
    };
    this.getEndLate = function()
    {
        return this._endLate;
    };
    this.setEndLate = function( endLate )
    {
        this._endLate = endLate;
    };
    this.getInactive = function()
    {
        return this._inactive;
    };
    this.setInactive = function( inactive )
    {
        this._inactive = inactive;
    };

    this.addToDb = function()
    {
        logger.info( this.__module(), "deleteFromDb()" );

        var requestContext      = {};
        requestContext["added"] = false;

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setPostData( "schedule=" + encodeURIComponent( Array2JSON( this.toJson() ) ) );
        request.setCallback( function( status, context, data )
        {
            if ( status )
            {
                logger.info( self.__module(), "addToDb.callback: added/changed schedule" );

                context["added"] = true;

                if ( data )
                {
                    self._id = data;
                    logger.warning( self.__module(), "addToDb.callback: added new schedule with id=" + self._id );
                }
            }
        } );
        if ( this._id == -1 )
        {
            request.send( "POST", "/api/schedules/addSchedule", false );
        }
        else
        {
            request.send( "POST", "/api/schedules/changeSchedule/" + this._id, false );
        }

        return requestContext["added"];
    };
    this.deleteFromDb = function()
    {
        logger.info( this.__module(), "deleteFromDb()" );

        var requestContext         = {};
        requestContext["deleted"]  = false;

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, data )
        {
            if ( status )
            {
                logger.info( self.__module(), "deleteFromDb.callback: deleted schedule" );

                context["deleted"] = true;
            }
        } );
        request.send( "GET", "/api/schedules/deleteSchedule/" + this._id, false );

        return requestContext["deleted"];
    };
}

function AminoPVRClass()
{
    var _generalConfig = null;

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
    };

    this.getGeneralConfig = function()
    {
        if ( this._generalConfig == null )
        {
            var requestContext  = {};
            var self            = this;

            logger.info( this.__module(), "getGeneralConfig: Retrieve general config" );

            var request = new JsonAjaxRequest();
            request.setContext( requestContext );
            request.setCallback( function( status, context, config ) { self._generalConfigCallback( status, context, config ); } );
            request.send( "GET", "/api/config/getGeneralConfig", false );
        }

        return this._generalConfig;
    };
    this._generalConfigCallback = function( status, context, config )
    {
        if ( status )
        {
            try
            {
                this._generalConfig = new AminoPVRGeneralConfig();
                this._generalConfig.fromJson( config );
            }
            catch ( e )
            {
                logger.error( this.__module(), "_generalConfigCallback: exception: " + e );
                this._generalConfig = null;
            }
        }
        else
        {
            logger.error( this.__module(), "_generalConfigCallback: Retrieving general config failed" );
        }
    };

    this.getChannelList = function( context, callback, async )
    {
        var requestContext         = {};
        requestContext["context"]  = context;
        requestContext["callback"] = callback;

        var self = this;

        logger.info( this.__module(), "getChannelList: Downloading channel list" );

        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, channels ) { self._channelListCallback( status, context, channels ); } );
        request.send( "GET", "/api/channels/getChannelList", async );
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
                    pvrChannels[i].fromJson( channels[i] );
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
    this.getChannelByIpPort = function( ip, port )
    {
        var requestContext = {};
        requestContext["channel"] = null;

        logger.info( this.__module(), "getChannelByIpPort: Downloading channel by ip=" + ip + " and port=" + port );

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, channel ) { self._channelCallback( status, context, channel ); } );
        request.send( "GET", "/api/channels/getChannelByIpPort/" + ip + "/" + port, false );

        return requestContext["channel"];
    };
    this._channelCallback = function( status, context, program )
    {
        if ( status )
        {
            try
            {
                context["channel"] = new AminoPVRChannel();
                context["channel"].fromJson( channel );

                logger.info( this.__module(), "_channelCallback: Downloaded channel" );

                if ( "callback" in context )
                {
                    context["callback"]( true, context["context"], context["channel"] );
                }
            }
            catch ( e )
            {
                logger.error( this.__module(), "_channelCallback: exception: " + e );
                if ( "callback" in context )
                {
                    context["callback"]( false, context["context"] );
                }
            }
        }
        else
        {
            logger.error( this.__module(), "_channelCallback: Downloading channel failed" );
            if ( "callback" in context )
            {
                context["callback"]( false, context["context"] );
            }
        }
    };
    this.getEpgProgramByOriginalId = function( originalId )
    {
        var requestContext = {};
        requestContext["program"] = null;

        logger.info( this.__module(), "getEpgProgramByOriginalId: Downloading program by originalId=" + originalId );

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, program ) { self._epgProgramCallback( status, context, program ); } );
        request.send( "GET", "/api/epg/getEpgProgramByOriginalId/" + originalId, false );

        return requestContext["program"];
    };
    this._epgProgramCallback = function( status, context, program )
    {
        if ( status )
        {
            try
            {
                context["program"] = new AminoPVREpgProgram();
                context["program"].fromJson( program );

                logger.info( this.__module(), "_epgProgramCallback: Downloaded program" );

                if ( "callback" in context )
                {
                    context["callback"]( true, context["context"], context["program"] );
                }
            }
            catch ( e )
            {
                logger.error( this.__module(), "_epgProgramCallback: exception: " + e );
                if ( "callback" in context )
                {
                    context["callback"]( false, context["context"] );
                }
            }
        }
        else
        {
            logger.error( this.__module(), "_epgProgramCallback: Downloading program failed" );
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
        request.setCallback( function( status, context, programs ) { self._nowNextProgramListCallback( status, context, programs ); } );
        request.send( "GET", "/api/epg/getNowNextProgramList", async );
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
                        pvrPrograms[epgId][i].fromJson( programs[epgId][i] );
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
            arguments += "count=" + count;
        }
        if ( arguments != "" )
        {
            arguments = "?" + arguments;
        }

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, recordings ) { self._recordingListCallback( status, context, recordings ); } );
        request.send( "GET", "/api/recordings/getRecordingList" + arguments, async );
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
                    pvrRecordings[i].fromJson( recordings[i] );
                }

                logger.info( this.__module(), "_recordingListCallback: Downloaded recording list; count = " + pvrRecordings.length );

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
    this.getRecordingById = function( recordingId )
    {
        var recording               = null;
        var requestContext          = {};
        requestContext["recording"] = recording;

        logger.info( this.__module(), "getRecordingById: Retrieve recording with id: " + recordingId );

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, recording )
        {
            if ( status )
            {
                try
                {
                    context["recording"] = new AminoPVRRecording();
                    context["recording"].fromJson( recording );
                }
                catch ( e )
                {
                    logger.error( this.__module(), "getRecordingById.callback: exception: " + e );
                }
            }
            else
            {
                logger.error( this.__module(), "getRecordingById.callback: Retrieving recording failed" );
            }
        } );
        request.send( "GET", "/api/recordings/getRecordingById/" + recordingId, false );

        return recording;
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
                    pvrRecordings[i].fromJson( recordings[i] );
                }

                logger.info( this.__module(), "_recordingListCallback: Downloaded recording list; count = " + pvrRecordings.length );

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
    this.getScheduleList = function( context, callback, async )
    {
        var requestContext         = {};
        requestContext["context"]  = context;
        requestContext["callback"] = callback;

        logger.info( this.__module(), "getScheduleList: Downloading schedule list" );

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, schedules ) { self._scheduleListCallback( status, context, schedules ); } );
        request.send( "GET", "/api/schedules/getScheduleList", async );
    };
    this._scheduleListCallback = function( status, context, schedules )
    {
        if ( status )
        {
            try
            {
                var pvrSchedules = [];
                for ( var i in schedules )
                {
                    pvrSchedules[i] = new AminoPVRSchedule();
                    pvrSchedules[i].fromJson( schedules[i] );
                }

                logger.info( this.__module(), "_scheduleListCallback: Downloaded schedule list; count = " + pvrSchedules.length );

                if ( "callback" in context )
                {
                    context["callback"]( true, context["context"], pvrSchedules );
                }
            }
            catch ( e )
            {
                logger.error( this.__module(), "_scheduleListCallback: exception: " + e );
                if ( "callback" in context )
                {
                    context["callback"]( false, context["context"] );
                }
            }
        }
        else
        {
            logger.error( this.__module(), "_scheduleListCallback: Downloading schedule list failed" );
            if ( "callback" in context )
            {
                context["callback"]( false, context["context"] );
            }
        }
    };
    this.getScheduleByTitleAndChannelId = function( title, channelId )
    {
        var requestContext = {};
        requestContext["schedule"] = null;

        logger.info( this.__module(), "getScheduleByTitleAndChannelId: Downloading schedule by title=" + title + " and port=" + channelId );

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, schedule ) { self._channelCallback( status, context, schedule ); } );
        request.send( "GET", "/api/schedules/getScheduleByTitleAndChannelId/" + encodeURIComponent( title ) + "/" + channelId, false );

        return requestContext["schedule"];
    };
    this._scheduleCallback = function( status, context, program )
    {
        if ( status )
        {
            try
            {
                context["schedule"] = new AminoPVRSchedule();
                context["schedule"].fromJson( schedule );

                logger.info( this.__module(), "_scheduleCallback: Downloaded schedule" );

                if ( "callback" in context )
                {
                    context["callback"]( true, context["context"], context["channel"] );
                }
            }
            catch ( e )
            {
                logger.error( this.__module(), "_scheduleCallback: exception: " + e );
                if ( "callback" in context )
                {
                    context["callback"]( false, context["context"] );
                }
            }
        }
        else
        {
            logger.error( this.__module(), "_scheduleCallback: Downloading schedule failed" );
            if ( "callback" in context )
            {
                context["callback"]( false, context["context"] );
            }
        }
    };
    this.getScheduledRecordingList = function( context, callback, async, offset, count )
    {
        var requestContext         = {};
        requestContext["context"]  = context;
        requestContext["callback"] = callback;

        logger.info( this.__module(), "getScheduledRecordingList: Downloading scheduled recording list" );

        var arguments = "";
        if ( offset != undefined )
        {
            arguments += "offset=" + offset + "&";
        }
        if ( count != undefined )
        {
            arguments += "count=" + count;
        }
        if ( arguments != "" )
        {
            arguments = "?" + arguments;
        }

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, recordings ) { self._scheduledRecordingListCallback( status, context, recordings ); } );
        request.send( "GET", "/api/schedules/getScheduledRecordingList" + arguments, async );
    };
    this._scheduledRecordingListCallback = function( status, context, recordings )
    {
        if ( status )
        {
            try
            {
                var pvrRecordings = [];
                for ( var i in recordings )
                {
                    pvrRecordings[i] = new AminoPVRRecording();
                    pvrRecordings[i].fromJson( recordings[i] );
                }

                logger.info( this.__module(), "_scheduledRecordingListCallback: Downloaded scheduled recording list; count = " + pvrRecordings.length );

                if ( "callback" in context )
                {
                    context["callback"]( true, context["context"], pvrRecordings );
                }
            }
            catch ( e )
            {
                logger.error( this.__module(), "_scheduledRecordingListCallback: exception: " + e );
                if ( "callback" in context )
                {
                    context["callback"]( false, context["context"] );
                }
            }
        }
        else
        {
            logger.error( this.__module(), "_scheduledRecordingListCallback: Downloading recording list failed" );
            if ( "callback" in context )
            {
                context["callback"]( false, context["context"] );
            }
        }
    };
}

var CONTROLLER_TYPE_CONTROLLER = 1;
var CONTROLLER_TYPE_RENDERER   = 2;

function AminoPVRController( type, handlerInst )
{
    this._type              = type;
    this._controllerHandler = handlerInst;
    this._controllerId      = -1;

    this._POLL_SHORT_INTERVAL = 100;
    this._POLL_LONG_INTERVAL  = 5000;

    this.__module = function()
    {
        return "aminopvr." + this.constructor.name;
    };

    this.init = function()
    {
        if ( this._controllerId == -1 )
        {
            logger.warning( this.__module(), "init: Initialize controller polling" );

            try
            {
                var self    = this;
                var request = new JsonAjaxRequest();
                request.setCallback( function( status, context, data )
                {
                    if ( status && data["id"] != -1 )
                    {
                        self._controllerId = data["id"];
                        window.setTimeout( function()
                        {
                            self._poll();
                        }, self._POLL_SHORT_INTERVAL );
                    }
                    else
                    {
                        window.setTimeout( function()
                        {
                            self._init();
                        }, self._POLL_LONG_INTERVAL );
                    }
                } );
                request.send( "GET", "/api/controller/init?type=" + this._type, true );
            }
            catch ( e )
            {
                logger.critical( this.__module(), "init: exception: " + e );
            }
        }
    };
    this.sendMessage = function( toId, message, context, callback, async )
    {
        var requestContext         = {};
        requestContext["context"]  = context;
        requestContext["callback"] = callback;

        logger.info( this.__module(), "sendMessage: send message from" + this._controllerId + " to " + toId );

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, data ) { self._sendMessageCallback( status, context, data ); } );
        request.setRequestHeader( "Content-Type", "application/x-www-form-urlencoded" );
        request.setPostData( "message=" + encodeURIComponent( Array2JSON( message ) ) );
        request.send( "POST", "/api/controller/sendMessage/" + this._controllerId + "/" + toId, async );
    };
    this._sendMessageCallback = function( status, context, data )
    {
        if ( status )
        {
            try
            {
                logger.info( this.__module(), "_sendMessageCallback: Message sent" );
                if ( ("callback" in context) && (context["callback"]) )
                {
                    context["callback"]( true, context["context"] );
                }
            }
            catch ( e )
            {
                logger.error( this.__module(), "_sendMessageCallback: exception: " + e );
                if ( ("callback" in context) && (context["callback"]) )
                {
                    context["callback"]( false, context["context"] );
                }
            }
        }
        else
        {
            logger.error( this.__module(), "_sendMessageCallback: Message not sent" );
            if ( ("callback" in context) && (context["callback"]) )
            {
                context["callback"]( false, context["context"] );
            }
        }
    };
    this.getListenerList = function( context, callback, async )
    {
        var requestContext         = {};
        requestContext["context"]  = context;
        requestContext["callback"] = callback;

        logger.info( this.__module(), "getListenerList: Downloading listener list" );

        var self    = this;
        var request = new JsonAjaxRequest();
        request.setContext( requestContext );
        request.setCallback( function( status, context, listeners ) { self._listenerListCallback( status, context, listeners ); } );
        request.send( "GET", "/api/controller/getListenerList", async );
    };
    this._listenerListCallback = function( status, context, listeners )
    {
        if ( status )
        {
            try
            {
                logger.info( this.__module(), "_listenerListCallback: Downloaded listener list; count = " + listeners.length );

                if ( ("callback" in context) && (context["callback"]) )
                {
                    context["callback"]( true, context["context"], listeners );
                }
            }
            catch ( e )
            {
                logger.error( this.__module(), "_listenerListCallback: exception: " + e );
                if ( ("callback" in context) && (context["callback"]) )
                {
                    context["callback"]( false, context["context"] );
                }
            }
        }
        else
        {
            logger.error( this.__module(), "_listenerListCallback: Downloading listener list failed" );
            if ( ("callback" in context) && (context["callback"]) )
            {
                context["callback"]( false, context["context"] );
            }
        }
    };

    this._poll = function()
    {
        if ( this._controllerId != -1 && this._controllerHandler != null )
        {
            try
            {
                var self    = this;
                var request = new JsonAjaxRequest();
                request.setCallback( function( status, context, data )
                {
                    if ( status )
                    {
                        try
                        {
                            self._controllerHandler._callback( data );
                            window.setTimeout( function()
                            {
                                self._poll();
                            }, self._POLL_SHORT_INTERVAL );
                        }
                        catch ( e )
                        {
                            logger.critical( self.__module(), "_poll.callback: exception: " + e );
                            window.setTimeout( function()
                            {
                                self._controllerId = -1;
                                self.init();
                            }, self._POLL_LONG_INTERVAL );
                        }
                    }
                    else
                    {
                        logger.critical( self.__module(), "_poll.callback: status: " + status + ", re-init" );
                        window.setTimeout( function()
                        {
                            self._controllerId = -1;
                            self.init();
                        }, self._POLL_LONG_INTERVAL );
                    }
                } );
                request.send( "GET", "/api/controller/poll?id=" + this._controllerId, true );
            }
            catch ( e )
            {
                logger.critical( this.__module(), "_poll: exception: " + e );
            }
        }
    };

}

/**
 * Converts the given data structure to a JSON string.
 * Argument: arr - The data structure that must be converted to JSON
 * Example: var json_string = array2json(['e', {pluribus: 'unum'}]);
 *          var json = array2json({"success":"Sweet","failure":false,"empty_array":[],"numbers":[1,2,3],"info":{"name":"Binny","site":"http:\/\/www.openjs.com\/"}});
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

var logger   = new LoggerClass();
var aminopvr = new AminoPVRClass();
