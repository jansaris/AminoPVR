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

function APIClass()
{
    this.setChannelInstance = function()
    {
        return {set_channel_instance};
    };
    this.playStreamAction1  = function( channel )
    {
        {play_action_1}( channel );
    };
    this.playStreamClass    = function( url, aa, local )
    {
        return new {play_stream_class}( url, aa, local );
    };
    this.playStreamAction2  = function( stream )
    {
        {play_action_2}( stream );
    };
    this.setChannelFunction = function( channel, aa )
    {
        {set_channel_instance}.{set_channel_function}( channel, aa )
    };
    this.debugFunction      = function( debug )
    {
        {debug_function}( debug );
    };
    this.keyEventFunction   = function( key )
    {
        {key_event_function}( key );
    };
    this.keyEventFunctionPtr = function()
    {
        return {key_event_function};
    };
    this.channelList        = function()
    {
        return {channel_list};
    };
}

function API_KeyboardEvent()
{
    this.keyCode  = 0;
    this.charCode = 0;
}

function API_ChannelClass()
{
    this.NameLong  = "";
    this.NameShort = "";
    this.EPGID1    = "";
    this.EPGID2    = "";
    this.Logo1     = "";
    this.Logo2     = "";
    this.Radio     = false;
    this.URL       = "";
    this.URLHD     = "";
    this.URLHDPlus = "";

    this.getChannel = function( channel )
    {
        if ( channel != null )
        {
            if ( channel.{channel_id_1} !== undefined )
            {
                this.EPGID1 = channel.{channel_id_1};
            }
            if ( channel.{channel_id_2} !== undefined )
            {
                this.EPGID2 = channel.{channel_id_2};
            }
            if ( channel.{channel_name_long} !== undefined )
            {
                this.NameLong = channel.{channel_name_long}["default"];
            }
            if ( channel.{channel_name_short} !== undefined )
            {
                this.NameShort = channel.{channel_name_short}["default"];
            }
            if ( channel.{channel_logo_1} !== undefined )
            {
                this.Logo1 = "{channel_logo_path}/" + channel.{channel_logo_1};
            }
            if ( channel.{channel_logo_2} !== undefined )
            {
                this.Logo2 = "{channel_thumb_path}/" + channel.{channel_logo_2};
            }
            if ( channel.{channel_radio} !== undefined )
            {
                this.Radio = channel.{channel_radio};
            }
            for ( var j = 0; j < channel.{channel_streams}.length; j++ )
            {
                if ( channel.{channel_streams}[j].{channel_url} !== undefined )
                {
                    if ( channel.{channel_streams}[j].{channel_url_hd} !== undefined && channel.{channel_streams}[j].{channel_url_hd} == 1 )
                    {
                        if ( channel.{channel_streams}[j].{channel_metadata} !== undefined && channel.{channel_streams}[j].{channel_metadata}["default"] == "HD+")
                        {
                            this.URLHDPlus = channel.{channel_streams}[j].{channel_url};
                        }
                        else
                        {
                            this.URLHD = channel.{channel_streams}[j].{channel_url};
                        }
                    }
                    else
                    {
                        this.URL = channel.{channel_streams}[j].{channel_url};
                    }
                }
            }
        }
    }
}
