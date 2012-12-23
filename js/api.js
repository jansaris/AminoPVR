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
    this.SetChannelInstance = function()
    {
        return {SetChannelInstance};
    };
    this.PlayStreamAction1  = function( channel )
    {
        {PlayStreamAction1}( channel );
    };
    this.PlayStreamClass    = function( url, aa, local )
    {
        return new {PlayStreamClass}( url, aa, local );
    };
    this.PlayStreamAction2  = function( stream )
    {
        {PlayStreamAction2}( stream );
    };
    this.SetChannelFunction = function( channel, aa )
    {
        {SetChannelInstance}.{SetChannelFunction}( channel, aa )
    };
    this.DebugFunction      = function( debug )
    {
        {DebugFunction}( debug );
    };
    this.KeyEventFunction   = function( key )
    {
        {KeyEventFunction}( key );
    };
    this.KeyEventFunctionPtr = function()
    {
        return {KeyEventFunction};
    };
    this.ChannelList        = function()
    {
        return {ChannelList};
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

    this.GetChannel = function( channel )
    {
        if ( channel != null )
        {
            if ( channel.{ChannelID1} !== undefined )
            {
                this.EPGID1 = channel.{ChannelID1};
            }
            if ( channel.{ChannelID2} !== undefined )
            {
                this.EPGID2 = channel.{ChannelID2};
            }
            if ( channel.{ChannelNameLong} !== undefined )
            {
                this.NameLong = channel.{ChannelNameLong}["default"];
            }
            if ( channel.{ChannelNameShort} !== undefined )
            {
                this.NameShort = channel.{ChannelNameShort}["default"];
            }
            if ( channel.{ChannelLogo1} !== undefined )
            {
                this.Logo1 = channel.{ChannelLogo1};
            }
            if ( channel.{ChannelLogo2} !== undefined )
            {
                this.Logo2 = channel.{ChannelLogo2};
            }
            if ( channel.{ChannelRadio} !== undefined )
            {
                this.Radio = channel.{ChannelRadio};
            }
            for ( var j = 0; j < channel.{ChannelStreams}.length; j++ )
            {
                if ( channel.{ChannelStreams}[j].{ChannelURL} !== undefined )
                {
                    if ( channel.{ChannelStreams}[j].{ChannelURLHD} !== undefined && channel.{ChannelStreams}[j].{ChannelURLHD} == 1 )
                    {
                        this.URLHD = channel.{ChannelStreams}[j].{ChannelURL};
                    }
                    else
                    {
                        this.URL = channel.{ChannelStreams}[j].{ChannelURL};
                    }
                }
            }
        }
    }
}

//function API_ChannelRadio( index )
//{
//    var radio = false;
//    if ( channel.{ChannelRadio} !== undefined )
//    {
//        radio = channel.{ChannelRadio};
//    }
//    return ( radio );
//}
//function API_ChannelStreams( index )
//{
//    streams = null;
//    if ( channel.{ChannelStreams} !== undefined )
//    {
//        streams = channel.{ChannelStreams};
//    }
//    return ( streams );
//}
//function API_ChannelStreamsURLHD( index, stream_index )
//{
//    url = "";
//    if ( channel.{ChannelStreams}[stream_index].{ChannelURLHD} !== undefined )
//    {
//        url = channel.{ChannelStreams}[stream_index].{ChannelURLHD};
//    }
//    return ( url );
//}
//function API_ChannelStreamsURL( index, stream_index )
//{
//    url = "";
//    if ( channel.{ChannelStreams}[stream_index].{ChannelURL} !== undefined )
//    {
//        url = channel.{ChannelStreams}[stream_index].{ChannelURL};
//    }
//    return ( url );
//}
//function API_ChannelID2( index )
//{
//    id = 0;
//    if ( channel.{ChannelID2} !== undefined )
//    {
//        id = channel.{ChannelID2};
//    }
//    return ( id );
//}
//function API_ChannelNameLong( index )
//{
//    name = "";
//    if ( channel.{ChannelNameLong} !== undefined )
//    {
//        name = channel.{ChannelNameLong}["default"];
//    }
//    return ( name );
//}
//function API_ChannelNameShort( index )
//{
//    name = "";
//    if ( channel.{ChannelNameShort} !== undefined )
//    {
//        name = channel.{ChannelNameShort}["default"];
//    }
//    return ( name );
//}
//function API_ChannelNameLogo1( index )
//{
//    logo = "";
//    if ( channel.{ChannelNameLogo1} !== undefined )
//    {
//        logo = channel.{ChannelNameLogo1}["default"];
//    }
//    return ( logo );
//}
//function API_ChannelNameLogo2( index )
//{
//    logo = "";
//    if ( channel.{ChannelNameLogo2} !== undefined )
//    {
//        logo = channel.{ChannelNameLogo2}["default"];
//    }
//    return ( logo );
//}
