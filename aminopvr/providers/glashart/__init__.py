"""
    This file is part of AminoPVR.
    Copyright (C) 2012  Ino Dekker

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from StringIO import StringIO
from aminopvr.providers.glashart.config import glashartConfig
from aminopvr.providers.glashart.epg import EpgProvider
from aminopvr.providers.glashart.wi import WebInterface
from aminopvr.tools import getPage
import aminopvr.providers
import gzip
import logging
import re

_logger = logging.getLogger( "aminopvr.providers.glashart" )

def RegisterProvider():
    _logger.info( "RegisterProvider" )
    aminopvr.providers.webInterface    = WebInterface
    aminopvr.providers.epgProvider     = EpgProvider
    #aminopvr.providers.contentProvider = ContentProvider

def indexPageParser():
    content, code, mime = getPage( glashartConfig.tvmenuIndexPath )
    if content:
        fileHandle  = gzip.GzipFile( fileobj=StringIO( content ) )
        fileContent = fileHandle.read()
        regExp      = {
                        "TITLE":      re.compile( r'\<title\>(?P<page_title>.*)\<\/title\>' ),
                        "STYLE":      re.compile( r'\<link rel=\'stylesheet\' type=\'text\/css\' href=\'(?P<css_filename>.*)\'\>\<\/link\>' ),
                        "JAVASCRIPT": re.compile( r'\<script type=\'text\/javascript\' src=\'(?P<js_filename>.*)\'\>\<\/script\>' )
                      }
        # "REPLACE_STYLE"                     => "<link rel='stylesheet' type='text/css' href='style.css'></link>",
        # "REPLACE_JAVASCRIPT"                => "<script type='text/javascript' src='js/api.js'/><script type='text/javascript' src='js/service.js'/><script type='text/javascript' src='js/stub.js'/><script type='text/javascript' src='js/proxy.js'/><script type='text/javascript' src='code.js'></script>",
        titleMatch  = regExp["TITLE"].search( fileContent )
        if titleMatch:
            _logger.info( "indexPageParser: found title: %s" % ( titleMatch.group( "page_title" ) ) )
            return titleMatch.group( "page_title" )
        else:
            _logger.warning( "indexPageParser: title not found!" )
    return ""

def codeJSParser():
    content, code, mime = getPage( glashartConfig.tvmenuCodeJsPath )
    if content:
        fileHandle  = gzip.GzipFile( fileobj=StringIO( content ) )
        fileContent = fileHandle.read()
        regExp = {
                    "CHANNEL_LIST_1":              r"(?P<channel_list>[A-Za-z]{1})\[[a-z]{1}\]=\{(?P<channel_number>[A-Za-z]{1}):[A-Za-z]{1},\s*(?P<channel_name_long>[A-Za-z]{1}):\{\"default\":\"Nederland 1\"\},\s*(?P<channel_name_short>[A-Za-z]{1}):\{\"default\":\"Nederland 1\"\},\s*(?P<channel_id_1>[A-Za-z]{1}):\"ned1\",\s*(?P<channel_id_2>[A-Za-z]{1}):\"ned1\",\s*(?P<channel_logo_1>[A-Za-z]{1}):\"ned1.png\",\s*(?P<channel_logo_2>[A-Za-z]{1}):\"ned1.png\",\s*(?P<channel_logo_3>[A-Za-z]{1}):\"ned1.png\",\s*(?P<prev_channel_number>[A-Za-z]{1}):[A-Za-z]{1},\s*(?P<channel_streams>[A-Za-z]{1}):\[\]\};",
                    #                                a          ={ } ;   a          .e                             =" igmp:/ / 224     .1         .3         .1         :12110     " ;   a          .ta           =[{ia: "103"}];  a          .u          =1;   a          .D                              =1;
                    "CHANNEL_LIST_2":              r"[A-Za-z]{1}=\{\};\s*[A-Za-z]{1}.(?P<channel_url>[A-Za-z]{1,2})=\"igmp:\/\/[0-9]{3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}\";\s*[A-Za-z]{1}.[A-Za-z]{1,2}=\[([^\]]*)\];\s*[A-Za-z]{1}.[A-Za-z]{1}=1;\s*[A-Za-z]{1}.(?P<channel_url_hd>[A-Za-z]{1})=1;",
                    #                                for( $              .tv.l            .push( b            ) ;e            .length;) x                                 [ e            .pop( ) ] =b            ;
                    "CHANNEL_LIST_3":              r"for\([\$A-Za-z]{1,2}.tv.[A-Za-z]{1,2}.push\([A-Za-z]{1,2}\);[A-Za-z]{1,2}.length;\)(?P<channel_id_list>[A-Za-z]{1,2})\[[A-Za-z]{1,2}.pop\(\)\]=[A-Za-z]{1,2};",
                    #                                B                            [ b          ] ={ h                              :b          ,   a                                 :{ " default" :" Radio 3FM" } ,   m                                  :{ " default" :" Radio 3FM" } ,   g                            :" radio3" ,   j                            :" radio3" ,   p                              :" radio3fm.png" ,   q                              :" radio3fm.png" ,   n                              :" radio3fm.png" ,   s                             :1,   k                                   :a       ,c:[]   } ;
                    "CHANNEL_LIST_4":              r"(?P<channel_list>[A-Za-z]{1})\[[A-Za-z]{1}\]=\{(?P<channel_number>[A-Za-z]{1}):[A-Za-z]{1},\s*(?P<channel_name_long>[A-Za-z]{1}):\{\"default\":\"Radio 3FM\"\},\s*(?P<channel_name_short>[A-Za-z]{1}):\{\"default\":\"Radio 3FM\"\},\s*(?P<channel_id_1>[A-Za-z]{1}):\"radio3\",\s*(?P<channel_id_2>[A-Za-z]{1}):\"radio3\",\s*(?P<channel_logo_1>[A-Za-z]{1}):\"radio3fm.png\",\s*(?P<channel_logo_2>[A-Za-z]{1}):\"radio3fm.png\",\s*(?P<channel_logo_3>[A-Za-z]{1}):\"radio3fm.png\",\s*(?P<channel_radio>[A-Za-z]{1}):1,\s*(?P<prev_channel_number>[A-Za-z]{1}):[a-z]{1}([^\}]+)\};",
                    #                                Gb                                    =f          ;B          [ a          ] .i                                   =f          ;   for( B          [ f          ] .k          =a             ;e          .length;) w          [ e          .pop( ) ] =f          ;J          .root
                    "CHANNEL_LIST_5":              r"(?P<last_channel_number>[A-Za-z]{1,2})=[A-Za-z]{1};[A-Za-z]{1}\[[A-Za-z]{1}\].(?P<next_channel_number>[A-Za-z]{1})=[A-Za-z]{1};\s*for\([A-Za-z]{1}\[[A-Za-z]{1}\].[A-Za-z]{1}=\s*[A-Za-z]{1};[A-Za-z]{1}.length;\)[A-Za-z]{1}\[[A-Za-z]{1}.pop\(\)\]=[A-Za-z]{1};[A-Za-z]{1}.root",
                    #                                window.clearInterval( e            ) ;p                               ( fb           ) ;var c            =new r            ( o.Og                       ) ;c            .u            =d            ( ) ;s                               ( c            ) ;window.setTimeout( function( ) { ga           ( ) } ,50)
                    "PLAY_STREAM_ACTIONS":         r"window.clearInterval\([A-Za-z]{1,2}\);(?P<play_action_1>[A-Za-z]{1,2})\([A-Za-z]{1,2}\);var [A-Za-z]{1,2}=new [A-Za-z]{1,2}\([A-Za-z]{1,2}.[A-Za-z]{1,2}\);[A-Za-z]{1,2}.[A-Za-z]{1,2}=[A-Za-z]{1,2}\(\);(?P<play_action_2>[A-Za-z]{1,2})\([A-Za-z]{1,2}\);window.setTimeout\(function\(\)\{[A-Za-z]{1,2}\(\)\},50\)",
                    #                                function Ce                                  ( a                                 ,b            ) {N            .call( this) ;if( b            ===undefined) b            =" " ;
                    "PLAY_STREAM_CLASS":           r"function (?P<play_stream_class>[A-Za-z]{1,2})\((?P<play_stream_url>[A-Za-z]{1,2}),[A-Za-z]{1,2}\){[A-Za-z]{1,2}.call\(this\);if\([A-Za-z]{1,2}===undefined\)[A-Za-z]{1,2}=\"\";",
                    "SET_CHANNEL_FUNCTION":        r"[A-Za-z]{1,2}.prototype.(?P<set_channel_function>[A-Za-z]{1,2})=function\([A-Za-z]{1,2},[A-Za-z]{1,2}\){if\(this.[A-Za-z]{1,2}\){window.clearTimeout\(this.[A-Za-z]{1,2}\);",
                    #                                this.l            .appendChild( b            ) ;b            =new O            ( o            .fh           ) ;b            .ua           =function( ) {G                                      .ka(
                    "SET_CHANNEL_INSTANCE":        r"this.[A-Za-z]{1,2}.appendChild\([A-Za-z]{1,2}\);[A-Za-z]{1,2}=new [A-Za-z]{1,2}\([A-Za-z]{1,2}.[A-Za-z]{1,2}\);[A-Za-z]{1,2}.[A-Za-z]{1,2}=function\(\){(?P<set_channel_instance>[A-Za-z]{1,2}).%s\(",
                    "CHANNEL_OBJECT":              r"document.cookie=\"channel=\"\+encodeURIComponent\(this.(?P<channel_object_1>[A-Za-z]{1,2}).(?P<channel_object_2>[A-Za-z]{1,2})\);",
                    "DEBUG_FUNCTION":              r"function (?P<debug_function>[A-Za-z]{1,2})\([A-Za-z]{1,2}\){if\(window.console\)window.console.log\(",
                    "INIT_FUNCTION":               r"for\(%s\(\"doRunAfterLoad\(\): \"\+[A-Za-z]{1,2}.length\);[A-Za-z]{1,2}.length;\)[A-Za-z]{1,2}.pop\(\)\(\)",
                    "LAST_JS_LINE":                r"[A-Za-z]{1,2}\(\);\s*%s\(\"initial buildMenu\(\) done.\"\);",
                    "KEY_EVENT_FUNCTION":          r"function (?P<key_event_function>[A-Za-z]{1,2})\([A-Za-z]{1,2}\)\{[A-Za-z]{1,2}\(\);[A-Za-z]{1,2}&&clearTimeout\([A-Za-z]{1,2}\);[A-Za-z]{1,2}=[A-Za-z]{1,2}.keyCode\|\|[A-Za-z]{1,2}.charCode;",
                    "PLAY_STREAM_FUNCTION_PART_1": r";function %s\([A-Za-z]{1,2},[A-Za-z]{1,2}",
                    #                                if( b          =this.fr           .exec( this.Ue           ) ) this.Ue           =" rtsp:/ / d-" + " abcdefghijklmnop" .charAt( uf           ( this,b            [ 1]) & 15) + " .zt6.nl/ " + b            [ 1] ;
                    "PLAY_STREAM_FUNCTION_PART_2": r"if\([A-Za-z]{1}=this.[A-Za-z]{1,2}.exec\(this.[A-Za-z]{1,2}\)\)this.[A-Za-z]{1,2}=\"rtsp:\/\/d-\"\+\"abcdefghijklmnop\".charAt\([A-Za-z]{1,2}\(this,[A-Za-z]{1,2}\[1\]\)&15\)\+\".zt6.nl\/\"\+[A-Za-z]{1,2}\[1\];",
                    "PROXY_OBJECT":                r"(ASTB|PVR|AVMedia|Browser|VideoDisplay)\.",
                    "REDIRECT_FIX":                r"if\s*\(([a-z]{1})\s*=\s*([a-z]{1}\.[a-z]{1})\.redirect\){"
                 }
        symbolNames = {}
        channelList1Match = re.compile( regExp["CHANNEL_LIST_1"] ).search( fileContent )
        if channelList1Match:
            symbolNames["channel_list"]         = channelList1Match.group( "channel_list" )
            symbolNames["channel_number"]       = channelList1Match.group( "channel_number" )
            symbolNames["channel_name_long"]    = channelList1Match.group( "channel_name_long" )
            symbolNames["channel_name_short"]   = channelList1Match.group( "channel_name_short" )
            symbolNames["channel_id_1"]         = channelList1Match.group( "channel_id_1" )
            symbolNames["channel_id_2"]         = channelList1Match.group( "channel_id_2" )
            symbolNames["channel_logo_1"]       = channelList1Match.group( "channel_logo_1" )
            symbolNames["channel_logo_2"]       = channelList1Match.group( "channel_logo_2" )
            symbolNames["channel_logo_3"]       = channelList1Match.group( "channel_logo_3" )
            symbolNames["prev_channel_number"]  = channelList1Match.group( "prev_channel_number" )
            symbolNames["channel_streams"]      = channelList1Match.group( "channel_streams" )

            # For the folloing matches I only need about 1000 characters starting from the start of this match
            channelListString = fileContent[channelList1Match.start():channelList1Match.start() + 1000]

            channelList2Match = re.compile( regExp["CHANNEL_LIST_2"] ).search( channelListString )
            if channelList2Match:
                symbolNames["channel_url"]    = channelList2Match.group( "channel_url" )
                symbolNames["channel_url_hd"] = channelList2Match.group( "channel_url_hd" )
            else:
                _logger.error( "codeJSParser: no match for CHANNEL_LIST_2" )
                return False

            channelList3Match = re.compile( regExp["CHANNEL_LIST_3"] ).search( channelListString )
            if channelList3Match:
                symbolNames["channel_id_list"] = channelList3Match.group( "channel_id_list" )
            else:
                _logger.error( "codeJSParser: no match for CHANNEL_LIST_3" )
                return False

            # Take the rest of the file starting from the first match
            channelListString = fileContent[channelList1Match.start():]

            channelList4Match = re.compile( regExp["CHANNEL_LIST_4"] ).search( channelListString )
            if channelList4Match:
                if ( channelList4Match.group( "channel_list" )        == symbolNames["channel_list"]       and
                     channelList4Match.group( "channel_number" )      == symbolNames["channel_number"]     and
                     channelList4Match.group( "channel_name_long" )   == symbolNames["channel_name_long"]  and
                     channelList4Match.group( "channel_name_short" )  == symbolNames["channel_name_short"] and
                     channelList4Match.group( "channel_id_1" )        == symbolNames["channel_id_1"]       and
                     channelList4Match.group( "channel_id_1" )        == symbolNames["channel_id_1"]       and
                     channelList4Match.group( "channel_logo_1" )      == symbolNames["channel_logo_1"]     and
                     channelList4Match.group( "channel_logo_2" )      == symbolNames["channel_logo_2"]     and
                     channelList4Match.group( "channel_logo_3" )      == symbolNames["channel_logo_3"]     and
                     channelList4Match.group( "prev_channel_number" ) == symbolNames["prev_channel_number"] ):
                    symbolNames["channel_radio"] = channelList4Match.group( "channel_radio" )
                else:
                    _logger.error( "codeJSParser: mismatch in CHANNEL_LIST_4 with earlier matches!" )
                    return False
            else:
                _logger.error( "codeJSParser: no match for CHANNEL_LIST_4" )
                return False

            channelList5Match = re.compile( regExp["CHANNEL_LIST_5"] ).search( channelListString )
            if channelList5Match:
                symbolNames["last_channel_number"] = channelList5Match.group( "last_channel_number" )
                symbolNames["next_channel_number"] = channelList5Match.group( "next_channel_number" )
            else:
                _logger.error( "codeJSParser: no match for CHANNEL_LIST_5" )
                return False
        else:
            _logger.error( "codeJSParser: no match for CHANNEL_LIST_1" )
            return False

        playStreamActionsMatch = re.compile( regExp["PLAY_STREAM_ACTIONS"] ).search( fileContent )
        if playStreamActionsMatch:
            symbolNames["play_action_1"] = playStreamActionsMatch.group( "play_action_1" );
            symbolNames["play_action_2"] = playStreamActionsMatch.group( "play_action_2" );
        else:
            _logger.error( "codeJSParser: no match for PLAY_STREAM_ACTIONS" )
            return False

        playStreamClassMatch = re.compile( regExp["PLAY_STREAM_CLASS"] ).search( fileContent )
        if playStreamClassMatch:
            symbolNames["play_stream_class"] = playStreamClassMatch.group( "play_stream_class" );
            symbolNames["play_stream_url"]   = playStreamClassMatch.group( "play_stream_url" );
        else:
            _logger.error( "codeJSParser: no match for PLAY_STREAM_CLASS" )
            return False

        setChannelFunctionMatch = re.compile( regExp["SET_CHANNEL_FUNCTION"] ).search( fileContent )
        if setChannelFunctionMatch:
            symbolNames["set_channel_function"] = setChannelFunctionMatch.group( "set_channel_function" );
            setChannelInstanceMatch = re.compile( regExp["SET_CHANNEL_INSTANCE"] % ( symbolNames["set_channel_function"] ) ).search( fileContent )
            if setChannelInstanceMatch:
                symbolNames["set_channel_instance"] = setChannelInstanceMatch.group( "set_channel_instance" );
            else:
                _logger.error( "codeJSParser: no match for SET_CHANNEL_FUNCTION" )
                return False
        else:
            _logger.error( "codeJSParser: no match for SET_CHANNEL_FUNCTION" )
            return False

        channelObjectMatch = re.compile( regExp["CHANNEL_OBJECT"] ).search( fileContent )
        if channelObjectMatch:
            symbolNames["channel_object_1"] = channelObjectMatch.group( "channel_object_1" );
            symbolNames["channel_object_2"] = channelObjectMatch.group( "channel_object_2" );
        else:
            _logger.error( "codeJSParser: no match for CHANNEL_OBJECT" )
            return False

        debugFunctionMatch = re.compile( regExp["DEBUG_FUNCTION"] ).search( fileContent )
        if debugFunctionMatch:
            symbolNames["debug_function"] = debugFunctionMatch.group( "debug_function" );

            initFunctionMatch = re.compile( regExp["INIT_FUNCTION"] % ( symbolNames["debug_function"] ) ).search( fileContent )
            if not initFunctionMatch:
                _logger.error( "codeJSParser: no match for INIT_FUNCTION" )
                return False

            lastJSLineMatch = re.compile( regExp["LAST_JS_LINE"] % ( symbolNames["debug_function"] ) ).search( fileContent )
            if not lastJSLineMatch:
                _logger.error( "codeJSParser: no match for LAST_JS_LINE" )
                return False
        else:
            _logger.error( "codeJSParser: no match for DEBUG_FUNCTION" )
            return False

        keyEventFunctionMatch = re.compile( regExp["KEY_EVENT_FUNCTION"] ).search( fileContent )
        if keyEventFunctionMatch:
            symbolNames["key_event_function"] = keyEventFunctionMatch.group( "key_event_function" );
        else:
            _logger.error( "codeJSParser: no match for KEY_EVENT_FUNCTION" )
            return False
    else:
        _logger.error( "codeJSParser: no file content!" )
#    "REPLACE_INIT_FUNCTION": "\${0};/* id_begin *//* id_end */",
#    "REPLACE_LAST_JS_LINE": "/* id_begin */try { PowerOn(); } catch( e ) { %s( \"Unable to call PowerOn(): \" + e ); }/* id_end */\${0}",
#    "REPLACE_SET_CHANNEL_FUNCTION": "\${0}/* id_begin */{var activeChannel = encodeURIComponent( this.%s.%s );window.setTimeout( function() { SetActiveChannel( encodeURIComponent( activeChannel ) ); }, 100 );}/* id_end */",
#    "REPLACE_PLAY_STREAM_FUNCTION_1": "\${0}/* id_begin */,localStream/* id_end */",
#    "REPLACE_PLAY_STREAM_FUNCTION_2": "/* id_begin */if ( !localStream ){\${0}}/* id_end */",
#    "REPLACE_CHANNEL_LOCK": "\${1}0,",
#    "REPLACE_PROXY_OBJECT": "\${1}Proxy.",
#    "REPLACE_REDIRECT_FIX": "if(\${2}.redirect){\${1}=\${2}.redirect;DebugLog( \"Redirecting to: \" + \${1} );",
