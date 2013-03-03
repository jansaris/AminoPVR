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

var RemoteServiceClassInst = null;

function RemoteServiceClass()
{
    this.API = new APIClass();

    this.pollServiceActive = false;

    this.pollRequest = null;
    this.statusRequest = null;
    this.channelRequest = null;

    this.debugLog = [];
    this.debugDiv = null;
    this.remoteDebug = false;
    this.remoteLogTimeout = null;
    this.remoteLogRequest = null;

    this.Init = function()
    {
        try
        {
            RemoteServiceClassInst = this;
            window.addEventListener( "load", function()
            {
                RemoteServiceClassInst.Onload();
            }, false );

            this.EnableRemoteDebug( true );
        }
        catch ( e )
        {
            this.API.DebugFunction( "RemoteServiceClass.Init: exception: " + e );
        }
    };

    this.PowerOn = function()
    {
        try
        {
            RemoteServiceClassInst = this;
            window.addEventListener( "keypress", function( key )
            {
                RemoteServiceClassInst.KeyListener( key );
            }, false );
            window.removeEventListener( "keypress", this.API.KeyEventFunctionPtr(), false );
        }
        catch ( e )
        {
            this.API.DebugFunction( "RemoteServiceClass.PowerOn: exception: " + e );
        }
//        if ( !window.ASTB && /Philips/.test( navigator.userAgent ) )
//        {
//            this.DebugLog( "Registering non-Amino playback functions." );
//
//            // Philips TV is HD capable.
//            $.hd = false;
//
//            // Play media
//            na = function( b )
//            {
//                try
//                {
//                    var urlParts = b.split( ';' );
//                    var url = urlParts[0].substring( 4 );
//
//                    if ( url.indexOf( 'igmp://' ) === 0 )
//                    {
//                        if ( (urlParts.length > 1) && (urlParts[1] == "rtpskip=yes") )
//                        {
//                            url = url.replace( 'igmp://', 'http://www.inodekker.com:4022/rtp/' );
//                        }
//                        else
//                        {
//                            url = url.replace( 'igmp://', 'http://www.inodekker.com:4022/udp/' );
//                        }
//                    }
//                    else if ( url.indexOf( 'rtsp://' ) === 0 )
//                    {
//                        url = url.replace( 'rtsp://', 'http://' );
//                        url = url.replace( ':8554/',  '/recordings/' );
//                    }
//
//                    DebugLog( "Going to play: " + url );
//
//                    var mediaObject = document.getElementById( 'media_object' );
//
//                    if ( mediaObject != null )
//                    {
//                        mediaObject.data              = url;
//                        mediaObject.onPlayStateChange = MediaObjectStateChange;
//                        mediaObject.play( 1 );
//                    }
//                }
//                catch ( e )
//                {
//                    DebugLog( "na: exception: " + e );
//                }
//            };
//
//            // Kill media
//            oa = function()
//            {
//                try
//                {
//                    var mediaObject = document.getElementById( 'media_object' );
//    
//                    if ( mediaObject != null )
//                    {
//                        mediaObject.stop();
//                    }
//                }
//                catch ( e )
//                {
//                    DebugLog( "oa: exception: " + e );
//                }
//            };
//        }
//        else if ( !window.ASTB )
//        {
//            $.hd = true;
//    
///*            // Play media
//            na = function( b )
//            {
//                var urlParts = b.split( ';' );
//                var url = urlParts[0].substring( 4 );
//
//                if ( url.indexOf( 'igmp://' ) === 0 )
//                {
//                    if ( (urlParts.length > 1) && (urlParts[1] == "rtpskip=yes") )
//                    {
//                        url = url.replace( 'igmp://', 'http://www.inodekker.com:4022/rtp/' );
//                    }
//                    else
//                    {
//                        url = url.replace( 'igmp://', 'http://www.inodekker.com:4022/udp/' );
//                    }
//                }
//                else if ( url.indexOf( 'rtsp://' ) === 0 )
//                {
//                    url = url.replace( 'rtsp://', 'http://' );
//                    url = url.replace( ':8554/',  '/recordings/' );
//                    url = url.replace( '.ts',     '.webm' );
//                }
//
//                try
//                {
//                    DebugLog( "Going to play: " + url );
//
//                    var videoObject = document.getElementById( 'video_object' );
//
//                    if ( videoObject != null )
//                    {
////                        videoObject.type = "video/webm";
//                        videoObject.src  = 'stream.m3u8?url=' + url;
//                        videoObject.load();
//                        videoObject.play();
//                    }
//                }
//                catch ( e )
//                {
//                    DebugLog( "na: exception: " + e );
//                }
//            };
//
//            // Kill media
//            oa = function()
//            {
//                var videoObject = document.getElementById( 'video_object' );
//
//                if ( videoObject != null )
//                {
//                    videoObject.pause();
//                }
//            };*/
//        }
    };

    this.Onload = function()
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
            this.API.DebugFunction( "RemoteServiceClass.Onload: exception: " + e );
        }

//        if ( !window.ASTB && /Philips/.test( navigator.userAgent ) )
//        {
//            try
//            {
//                // Set body size to 1280x720
//                document.body.style.width  = "1280px";
//                document.body.style.height = "720px";
//
//                var mediaObject = document.createElement( 'object' );
//
//                mediaObject.setAttribute( 'id',     'media_object' );
//                mediaObject.setAttribute( 'type',   'video/mpeg' );
//                mediaObject.setAttribute( 'width',  '1280' );
//                mediaObject.setAttribute( 'height', '720' );
//
//                document.body.appendChild( mediaObject );
//            }
//            catch ( e )
//            {
//                this.DebugLog( "RemoteServiceClass.Onload: exception: " + e );
//            }
//
//            window.setTimeout( this.ModifyStyles, 5000 );
//        }
//        else if ( !window.ASTB )
//        {
//            this.DebugLog( "Enable Debug Logging." );
//            this.debugDiv.style.display = "block";
//
//            try
//            {
//                // Set body size to 1280x720
//                document.body.style.width  = "1280px";
//                document.body.style.height = "720px";
//
////                var videoObject = document.createElement( 'video' );
//
////                videoObject.setAttribute( 'id',       'video_object' );
////                videoObject.setAttribute( 'width',    '1280' );
////                videoObject.setAttribute( 'height',   '720' );
//////                videoObject.setAttribute( 'autoplay', 'autoplay' );
//
////                document.body.appendChild( videoObject );
//            }
//            catch ( e )
//            {
//                this.DebugLog( "RemoteServiceClass.Onload: exception: " + e );
//            }
//
////            window.setTimeout( this.ModifyStyles, 5000 );
//        }

        RemoteServiceClassInst = this;
        window.setTimeout( function()
        {
            RemoteServiceClassInst.Poll();
        }, 100 );
    };

    this.Poll = function()
    {
        if ( !this.pollServerActive )
        {
            this.API.DebugFunction( "RemoteServiceClass.Poll: Starting polling service" );
            this.pollServerActive = true;

            try
            {
                RemoteServiceClassInst = this;
                this.pollRequest = new XMLHttpRequest();
                this.pollRequest.open( "GET", "/aminopvr/api/stb/poll?init", true );
                this.pollRequest.onreadystatechange = this.PollStateChange;
                this.pollRequest.send();
            }
            catch ( e )
            {
                this.pollRequest = false;
                this.DebugLog( "RemoteServiceClass.Poll: exception: " + e );
            }
        }
        else
        {
            try
            {
                RemoteServiceClassInst = this;
                this.pollRequest = new XMLHttpRequest();
                this.pollRequest.open( "GET", "/aminopvr/api/stb/poll", true );
                this.pollRequest.onreadystatechange = this.PollStateChange;
                this.pollRequest.send();
            }
            catch ( e )
            {
                this.pollRequest = false;
                this.DebugLog( "RemoteServiceClass.Poll: exception: " + e );
            }
        }
    };

    this.PollStateChange = function()
    {
        if ( RemoteServiceClassInst.pollRequest.readyState == 4 )
        {
            try
            {
                if ( RemoteServiceClassInst.pollRequest.responseText.length > 0 )
                {
                    var responseItem = eval( '(' + RemoteServiceClassInst.pollRequest.responseText + ')' );
                    if ( responseItem['status'] == 'success' )
                    {
                    	if ( responseItem['data']['type'] == 'command' )
                    	{
                        	if ( responseItem['data']['command'] == 'show_osd' )
                        	{
                            	RemoteServiceClassInst.DebugLog( "RemoteServiceClass.PollStateChange: command: show_osd." );
//                                RemoteServiceClassInst.API.SetChannelInstance().$(5000);
	                        }
    	                    else if ( responseItem['data']['command'] == 'play_stream' )
        	                {
            	                RemoteServiceClassInst.DebugLog( "RemoteServiceClass.PollStateChange: command: play_stream: url=" + responseItem['data']['url'] );

                	            RemoteServiceClassInst.API.PlayStreamAction1( RemoteServiceClassInst.API.SetChannelInstance() );
                    	        b = new RemoteServiceClassInst.API.PlayStreamClass( responseItem['data']['url'], "", true );
                        	    RemoteServiceClassInst.API.PlayStreamAction2( b );
	                        }
    	                    else if ( responseItem['data']['command'] == 'get_channel_list' )
        	                {
            	                window.setTimeout( function()
                	            {
                    	            RemoteServiceClassInst.SendChannelList();
                        	    }, 5000 );
	                        }
    	                    else if ( responseItem['data']['command'] == 'remote_debug' )
        	                {
            	                if ( !RemoteServiceClassInst.remoteDebug )
                	            {
                    	            RemoteServiceClassInst.EnableRemoteDebug( true );
                        	    }
	                            else
    	                        {
        	                        RemoteServiceClassInst.EnableRemoteDebug( false );
            	                }
                	        }
                    	    else if ( responseItem['data']['command'] == 'debug' )
                        	{
                            	if ( RemoteServiceClassInst.debugDiv !== undefined && RemoteServiceClassInst.debugDiv != null )
	                            {
    	                            if ( RemoteServiceClassInst.debugDiv.style.display == "none" )
        	                        {
            	                        RemoteServiceClassInst.DebugLog( "RemoteServiceClass.PollStateChange: Enable Debug Logging." );
                	                    RemoteServiceClassInst.debugDiv.style.display = "block";
                    	            }
                        	        else
                            	    {
                                	    RemoteServiceClassInst.DebugLog( "RemoteServiceClass.PollStateChange: Disable Debug Logging." );
                                    	RemoteServiceClassInst.debugDiv.style.display = "none";
	                                }
    	                        }
        	                }
            	            else
                	        {
                    	        RemoteServiceClassInst.DebugLog( "RemoteServiceClass.PollStateChange: other command: " + responseItem['command'] );
                        	}
	                    }
    	                else if ( responseItem['data']['type'] == 'channel' )
        	            {
            	            RemoteServiceClassInst.API.SetChannelFunction( responseItem['channel'], 0 );
                	    }
                    	else if ( responseItem['data']['type'] == 'key' )
	                    {
    	                    evt          = new API_KeyboardEvent;
        	                evt.keyCode  = responseItem['data']['key'];
            	            RemoteServiceClassInst.DebugLog( "RemoteServiceClass.PollStateChange: key: " + responseItem['data']['key'] );
                	        RemoteServiceClassInst.KeyListener( evt );
                    	}
	                    else if ( responseItem['data']['type'] == 'unknown_message' )
    	                {
        	                RemoteServiceClassInstDebugLog( "RemoteServiceClass.PollStateChange: unknown message received." );
            	        }
                	    else if ( responseItem['data']['type'] == 'timeout' )
                    	{
//                      	  RemoteServiceClassInst.DebugLog( "RemoteServiceClass.PollStateChange: timeout." );
	                    }
    	                else
        	            {
//          	              RemoteServiceClassInst.API.DebugFunction( "RemoteServiceClass.PollStateChange: " + responseItem );
                	    }
                	}
                }

                window.setTimeout( function()
                {
                    RemoteServiceClassInst.Poll();
                }, 100 );
            }
            catch ( e )
            {
                RemoteServiceClassInst.API.DebugFunction( "RemoteServiceClass.PollStateChange: exception: " + e + ", responseText: " + RemoteServiceClassInst.pollRequest.responseText );
                RemoteServiceClassInst.DebugLog( "RemoteServiceClass.PollStateChange: exception: " + e + ", responseText: " + RemoteServiceClassInst.pollRequest.responseText );
                window.setTimeout( function()
                {
                    RemoteServiceClassInst.Poll();
                } , 5000 );
            }

            RemoteServiceClassInst.pollRequest = false;
        }
    };

    this.SetActiveChannel = function( channel )
    {
        try
        {
            this.DebugLog( "RemoteServiceClass.SetActiveChannel: " + channel );

            RemoteServiceClassInst = this;
            this.statusRequest = new XMLHttpRequest();
            this.statusRequest.onreadystatechange = function()
            {
                if ( (this.readyState == 4) && (this.status == 200) )
                {
                    RemoteServiceClassInst.DebugLog( "RemoteServiceClass.SetActiveChannel.onreadystatechange: done: " + this.responseText );
                }
            };
            this.statusRequest.open( "GET", "/aminopvr/api/stb/setActiveChannel?channel=" + channel, true );
            this.statusRequest.send();
        }
        catch ( e )
        {
            this.statusRequest = false;
            this.DebugLog( "RemoteServiceClass.SetActiveChannel: exception: " + e );
        }
    };

    this.SendChannelList = function()
    {
        try
        {
//            var channelList = "[";
//            for ( var i = 0; i < this.API.ChannelList().length; i++ )
//            {
//                if ( this.API.ChannelList()[i] != null )
//                {
//                    var channel = new API_ChannelClass();
//                    channel.GetChannel( this.API.ChannelList()[i] );
//                    if ( channel.Radio != true )
//                    {
//                        if ( channelList != "[" )
//                        {
//                            channelList += ",";
//                        }
//
//                        var channelStreams = "[";
//                        if ( channel.URLHD != "" )
//                        {
//                            channelStreams += "{\"url\":\"" + channel.URLHD + "\",\"is_hd\":" + 1 + "}";
//                        }
//                        if ( channelStreams != "[" )
//                        {
//                            channelStreams += ",";
//                        }
//                        if ( channel.URL != "" )
//                        {
//                            channelStreams += "{\"url\":\"" + channel.URL + "\",\"is_hd\":" + 0 + "}";
//                        }
//                        channelStreams += "]";
//                        channelList    += "{\"id\":" + i + ",\"epg_id\":\"" + channel.EPGID2 + "\",\"name\":\"" + channel.NameLong + "\",\"name_short\":\"" + channel.NameShort + "\",\"logo\":\"" + channel.Logo1 + "\",\"thumbnail\":\"" + channel.Logo2 + "\",\"streams\":" + channelStreams + "}";
//                    }
//                }
//            }
//            channelList += "]";

            channels = []
            for ( var i = 0; i < this.API.ChannelList().length; i++ )
            {
                if ( this.API.ChannelList()[i] != null )
                {
                    var channel = new API_ChannelClass();
                    channel.GetChannel( this.API.ChannelList()[i] );
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

            this.DebugLog( "RemoteServiceClass.SendChannelList" );

            RemoteServiceClassInst = this;
            this.channelRequest = new XMLHttpRequest();
            this.channelRequest.onreadystatechange = function()
            {
                if ( (this.readyState == 4) && (this.status == 200) )
                {
                    RemoteServiceClassInst.DebugLog( "RemoteServiceClass.SendChannelList.onreadystatechange: done: " + this.responseText );
                }
            };
            this.channelRequest.open( "POST", "/aminopvr/api/stb/setChannelList", true );
            this.channelRequest.setRequestHeader( "Content-type", "application/x-www-form-urlencoded" );
            this.channelRequest.send( "channelList=" + encodeURIComponent( channelList ) );
        }
        catch ( e )
        {
            this.channelRequest = false;
            this.DebugLog( "RemoteServiceClass.SendChannelList: exception: " + e );
        }
    };

    this.KeyListener = function( b )
    {
        key = b.keyCode || b.charCode;
        this.DebugLog( "RemoteServiceClass.KeyListener: key=" + key );

//        if ( !window.ASTB && /Philips/.test( navigator.userAgent ) )
//        {
//            try
//            {
//                switch ( key )
//                {
//                    case VK_0:
//                        key = 10588;
//                        break;
//                    case VK_1:
//                        key = 10589;
//                        break;
//                    case VK_2:
//                        key = 10590;
//                        break;
//                    case VK_3:
//                        key = 10591;
//                        break;
//                    case VK_4:
//                        key = 10592;
//                        break;
//                    case VK_5:
//                        key = 10593;
//                        break;
//                    case VK_6:
//                        key = 10594;
//                        break;
//                    case VK_7:
//                        key = 10595;
//                        break;
//                    case VK_8:
//                        key = 10596;
//                        break;
//                    case VK_9:
//                        key = 10597;
//                        break;
//
//                    case VK_RED:
//                        key = 8512;
//                        break;
//                    case VK_GREEN:
//                        key = 8513;
//                        break;
//                    case VK_YELLOW:
//                        key = 8514;
//                        break;
//                    case VK_BLUE:
//                        key = 8515;
//                        break;
//
//                    case VK_LEFT:
//                        key = 37;
//                        break;
//                    case VK_UP:
//                        key = 38;
//                        break;
//                    case VK_RIGHT:
//                        key = 39;
//                        break;
//                    case VK_DOWN:
//                        key = 40;
//                        break;
//
//                    case VK_ENTER:
//                        key = 13;
//                        break;
//                    case VK_BACK:
//                        key = 8568;
//                        break;
//
//                    case VK_PLAY:
//                        key = 8499;
//                        break;
//                    case VK_PAUSE:
//                        key = 8504;
//                        break;
//                    case VK_STOP:
//                        key = 8501;
//                        break;
//                    case VK_FAST_FWD:
//                        key = 8500;
//                        break;
//                    case VK_REWIND:
//                        key = 8502;
//                        break;
//                }
//
//                b = new keyboardEvent;
//                b.keyCode = key;
//            }
//            catch ( e )
//            {
//                DebugLog( "KeyListener: " + e );
//            }
//        }

        try
        {
            this.API.KeyEventFunction( b );
        }
        catch ( e )
        {
            this.DebugLog( "RemoteServiceClass.KeyListener: exception: " + e );
        }
    };

    this.EnableRemoteDebug = function( enable )
    {
        this.remoteDebug = enable;

        if ( enable )
        {
            if ( this.debugDiv != null && this.debugDiv !== undefined )
            {
                if ( this.debugDiv.style.display == "block" )
                {
                    this.DebugLog( "Disable Debug Logging." );
                    this.debugDiv.style.display = "none";
                }
            }

            RemoteServiceClassInst = this;
            this.remoteLogTimeout = window.setTimeout( function()
            {
                RemoteServiceClassInst.SendDebugLog();
            }, 5000 );
        }
        else
        {
            if ( this.remoteLogTimeout )
            {
                window.clearTimeout( this.remoteLogTimeout );
            }
        }
    };

    this.DebugLog = function( log_text )
    {
        try
        {
            if ( this.remoteDebug )
            {
                if ( this.debugLog.length > 50 )
                {
                    if ( this.remoteLogTimeout )
                    {
                        window.clearTimeout( this.remoteLogTimeout );
                    }
                    this.SendDebugLog();
                }
            }
            else
            {
                if ( this.debugLog.length >= 20 )
                {
                    this.debugLog.splice( 0, this.debugLog.length - 19 );
                }
            }

            var logItem = {
                              timestamp: (new Date).getTime(),
                              level:     1,
                              log_text:  log_text
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
//                    this.debugDiv.innerHTML = html;
                }
            }
        }
        catch ( e )
        {
            if ( window.console )
            {
                window.console.log( "RemoteServiceClass.DebugLog: exception: " + e );
                window.console.log( "[1] " + (new Date).getTime() + ": " + log_text )
            }
//            if ( this.API.DebugFunction !== undefined )
//            {
//                this.API.DebugFunction( "DebugLog: exception: " + e );
//                this.API.DebugFunction( "[1] " + (new Date).getTime() + ": " + log_text );
//            }
        }
    };

    this.SendDebugLog = function()
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
    
                    RemoteServiceClassInst = this;
                    this.remoteLogRequest = new XMLHttpRequest;
                    this.remoteLogRequest.onreadystatechange = function()
                    {
                        if ( (this.readyState == 4) && (this.status == 200) )
                        {
                            remoteLogTimeout = window.setTimeout( function()
                            {
                                RemoteServiceClassInst.SendDebugLog();
                            }, 5000 );
                        }
                    };
                    this.remoteLogRequest.open( "POST", "/aminopvr/api/stb/postLog", true );
                    this.remoteLogRequest.setRequestHeader( "Content-Type", "application/x-www-form-urlencoded" );
                    this.remoteLogRequest.send( "logData=" + encodeURIComponent( debugLogText ) );
                }
                else
                {
                    RemoteServiceClassInst = this;
                    window.setTimeout( function()
                    {
                        RemoteServiceClassInst.SendDebugLog();
                    }, 5000 );
                }
            }
            catch ( e )
            {
                this.API.DebugFunction( "RemoteServiceClass.SendDebugLog: exception: " + e );
            }
        }
    };

//    this.ChangeCSS = function( theClass, element, value )
//    {
//        //Last Updated on July 4, 2011
//        //documentation for this script at
//        //http://www.shawnolson.net/a/503/altering-css-class-attributes-with-javascript.html
//        var cssRules;
//
//        for ( var S = 0; S < document.styleSheets.length; S++ )
//        {
//            try
//            {
//                document.styleSheets[S].insertRule( theClass + ' { ' + element + ': ' + value + '; }', document.styleSheets[S][cssRules].length );
//            }
//            catch ( err )
//            {
//                try
//                {
//                    document.styleSheets[S].addRule( theClass, element + ': ' + value + ';' );
//                }
//                catch ( err )
//                {
//                    try
//                    {
//                        if ( document.styleSheets[S]['rules'] )
//                        {
//                            cssRules = 'rules';
//                        }
//                        else if ( document.styleSheets[S]['cssRules'] )
//                        {
//                            cssRules = 'cssRules';
//                        }
//                        else
//                        {
//                            //no rules found... browser unknown
//                        }
//
//                        for ( var R = 0; R < document.styleSheets[S][cssRules].length; R++ )
//                        {
//                            if ( document.styleSheets[S][cssRules][R].selectorText == theClass )
//                            {
//                                if ( document.styleSheets[S][cssRules][R].style[element] )
//                                {
//                                    document.styleSheets[S][cssRules][R].style[element] = value;
//                                    break;
//                                }
//                            }
//                        }
//                    }
//                    catch ( err )
//                    {
//                        this.DebugLog( "ChangeCSS: exception: " + err );
//                    }
//                }
//            }
//        }
//    };

//    this.ModifyStyles = function()
//    {
//        try
//        {
//            var channelBoxContainer        = document.getElementById( 'channelBoxContainer' );
//            var channelBox                 = document.getElementById( 'channelBox' );
//            if ( channelBoxContainer != null )
//            {
//                channelBoxContainer.style.top       = "0px";
//                channelBoxContainer.style.left      = "0px";
//                channelBoxContainer.style.width     = "1280px";
//                channelBoxContainer.style.height    = "720px";
//
//                var colorKeyBar                     = channelBoxContainer.childNodes[1];
//
//                if ( colorKeyBar != null )
//                {
//                    colorKeyBar.style.top           = "649px";
//                    colorKeyBar.style.width         = "1172px";
//
//                    var key2 = colorKeyBar.childNodes[1];
//                    var key3 = colorKeyBar.childNodes[2];
//                    var key4 = colorKeyBar.childNodes[3];
//                    var key5 = colorKeyBar.childNodes[4];
//
//                    if ( key2 != null )
//                    {
//                        key2.style.left = "198px";
//                    }
//                    if ( key3 != null )
//                    {
//                        key3.style.left = "521px";
//                    }
//                    if ( key4 != null )
//                    {
//                        key4.style.left = "784px";
//                    }
//                    if ( key5 != null )
//                    {
//                        key5.style.left = "1087px";
//                    }
//                }
//            }
//            if ( channelBox != null )
//            {
//                channelBox.style.top                = "538px";
//                channelBox.style.width              = "1208px";
//
//                var programBackground               = channelBox.childNodes[3];
//                var clock                           = channelBox.childNodes[4];
//
//                if ( programBackground != null )
//                {
//                    programBackground.style.width   = "1044px";
//
//                    var rightArrow                  = programBackground.childNodes[1];
//                    if ( rightArrow != null )
//                    {
//                        rightArrow.style.left       = "1034px";
//                    }
//                }
//                if ( clock != null )
//                {
//                    clock.style.width               = "1178px";
//                }
//            }
//
//            ChangeCSS( "quicknavigation", "top",  "298px" );
//            ChangeCSS( "quicknavigation", "left", "551px" );
//        }
//        catch ( e )
//        {
//            DebugLog( "ModifyStyles: exception: " + e );
//        }
//    };

//    this.MediaObjectStateChange = function( playState )
//    {
//        try
//        {
//            var mediaObject = document.getElementById( 'media_object' );
//            if ( mediaObject != null )
//            {
//                switch ( mediaObject.playState )
//                {
//                    case 0: // stopped
//                        DebugLog( "MediaObjectStateChange: Stopped" );
//                        break;
//                    case 1: // playing
//                        DebugLog( "MediaObjectStateChange: Playing" );
//                        break;
//                    case 2: // paused
//                        DebugLog( "MediaObjectStateChange: Paused" );
//                        break;
//                    case 3: // connecting
//                        DebugLog( "MediaObjectStateChange: Connecting" );
//                        break;
//                    case 4: // buffering
//                        DebugLog( "MediaObjectStateChange: Buffering" );
//                        break;
//                    case 5: // finished
//                        DebugLog( "MediaObjectStateChange: Finished" );
//                        break;
//                    case 6: // error
//                        DebugLog( "MediaObjectStateChange: Error" );
//                        break;
//                    default:
//                        DebugLog( "MediaObjectStateChange: Unknown State" );
//                        break;
//                }
//            }
//        }
//        catch ( err )
//        {
//            DebugLog( "MediaObjectStateChange: exception: " + err );
//        }
//    };

}

var RemoteService = new RemoteServiceClass();
RemoteService.Init();

function PowerOn()
{
    if ( RemoteService != null )
    {
        RemoteService.PowerOn();
    }
}
function SetActiveChannel( channel )
{
    if ( RemoteService != null )
    {
        RemoteService.SetActiveChannel( channel );
    }
}
function DebugLog( log_text )
{
    if ( RemoteService != null )
    {
        RemoteService.DebugLog( log_text );
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
