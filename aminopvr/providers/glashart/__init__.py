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
from aminopvr.const import DATA_ROOT
from aminopvr.db import DBConnection
from aminopvr.providers.glashart.config import glashartConfig
from aminopvr.providers.glashart.epg import EpgProvider
from aminopvr.providers.glashart.page import PageSymbol
from aminopvr.providers.glashart.wi import WebInterface
from aminopvr.timer import Timer
from aminopvr.tools import getPage, Singleton
import aminopvr.providers
import datetime
import gzip
import logging
import os
import re
import threading
import time

_logger = logging.getLogger( "aminopvr.providers.glashart" )

def RegisterProvider():
    _logger.info( "RegisterProvider" )
    aminopvr.providers.webInterface    = WebInterface
    aminopvr.providers.epgProvider     = EpgProvider
    aminopvr.providers.contentProvider = ContentProvider

class ContentProvider( threading.Thread ):
    __metaclass__ = Singleton

    _logger = logging.getLogger( "aminopvr.providers.glashart.ContentProvider" )

    _timedeltaRegex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')

    def __init__( self ):
        threading.Thread.__init__( self )

        self._logger.debug( "ContentProvider" )

        now          = datetime.datetime.now()
        grabTime     = datetime.datetime.combine( datetime.datetime.today(), datetime.datetime.strptime( glashartConfig.grabContentTime, "%H:%M" ).timetz() )
        grabInterval = ContentProvider._parseTimedetla( glashartConfig.grabContentInterval )
        while grabTime < now:
            grabTime = grabTime + grabInterval

        self._logger.warning( "Starting Content grab timer @ %s with interval %s" % ( grabTime, grabInterval ) )

        self._running = True
        self._event   = threading.Event()
        self._event.clear()

        self._timer = Timer( [ { "time": grabTime, "callback": self._timerCallback, "callbackArguments": None } ], pollInterval=10.0, recurrenceInterval=grabInterval )

    def requestContentUpdate( self, wait=False ):
        if not self._event.isSet():
            self._event.set()
            if wait:
                while self._event.isSet():
                    time.sleep( 1.0 )
            return True
        else:
            self._logger.warning( "Content update in progress: skipping request" )
            return False

    def stop( self ):
        self._logger.warning( "Stopping ContentProvider" )
        self._timer.stop()
        self._running = False
        self._event.set()
        self.join()

    def run( self ):
        while self._running:
            self._event.wait()
            if self._running:
                self._translateContent()
            self._event.clear()

    @staticmethod
    def _parseTimedetla( timeString ):
        parts = ContentProvider._timedeltaRegex.match( timeString )
        if not parts:
            return
        parts      = parts.groupdict()
        timeParams = {}
        for ( name, param ) in parts.iteritems():
            if param:
                timeParams[name] = int( param )
        return datetime.timedelta( **timeParams )

    def _timerCallback( self, event, arguments ):
        if event == Timer.TIME_TRIGGER_EVENT:
            self._logger.warning( "Time to grab Content." )
            self.requestContentUpdate( True )

    def _translateContent( self ):
        indexContent, title, codeJsPath, styleCssPath = self._parseIndexPage()
        if title and indexContent:
            codeJsContent, symbolNames = self._parseCodeJs( codeJsPath )
            if codeJsContent:
                indexContent    = self._modifyIndexPage( indexContent )
                codeJsContent   = self._modifyCodeJs( codeJsContent, symbolNames )
                styleCssContent = self._getStyleCss( styleCssPath )
                apiJsContent    = self._modifyApiJs( symbolNames )
                if indexContent and codeJsContent and styleCssContent and apiJsContent:
                    self._logger.warning( "_translateContent: content translated: title=%s" % ( title ) )
                    conn = DBConnection()

                    if conn:
                        row = conn.execute( "SELECT * FROM glashart_pages WHERE page=?", ( "index.xhtml", ) )
                        if row:
                            conn.execute( "UPDATE glashart_pages SET content=? WHERE page=?", ( indexContent, "index.xhtml" ) )
                        else:
                            conn.insert( "INSERT INTO glashart_pages (page, content) VALUES (?, ?)", ( "index.xhtml", indexContent ) )

                        row = conn.execute( "SELECT * FROM glashart_pages WHERE page=?", ( "code.js", ) )
                        if row:
                            conn.execute( "UPDATE glashart_pages SET content=? WHERE page=?", ( codeJsContent, "code.js" ) )
                        else:
                            conn.insert( "INSERT INTO glashart_pages (page, content) VALUES (?, ?)", ( "code.js", codeJsContent ) )

                        row = conn.execute( "SELECT * FROM glashart_pages WHERE page=?", ( "style.css", ) )
                        if row:
                            conn.execute( "UPDATE glashart_pages SET content=? WHERE page=?", ( styleCssContent, "style.css" ) )
                        else:
                            conn.insert( "INSERT INTO glashart_pages (page, content) VALUES (?, ?)", ( "style.css", styleCssContent ) )

                        row = conn.execute( "SELECT * FROM glashart_pages WHERE page=?", ( "api.js", ) )
                        if row:
                            conn.execute( "UPDATE glashart_pages SET content=? WHERE page=?", ( apiJsContent, "api.js" ) )
                        else:
                            conn.insert( "INSERT INTO glashart_pages (page, content) VALUES (?, ?)", ( "api.js", apiJsContent ) )
                        # TODO: write symbol table to db
                if symbolNames:
                    conn = DBConnection()
                    if conn:
                        PageSymbol.addAllDictToDb( conn, symbolNames )

    def _parseIndexPage( self ):
        content, _, _ = getPage( glashartConfig.tvmenuIndexPath )
        if content:
            title        = None
            codeJsPath   = None
            styleCssPath = None

            fileHandle  = gzip.GzipFile( fileobj=StringIO( content ) )
            fileContent = fileHandle.read()
            regExp      = {
                            "TITLE":      r"\<title\>(?P<page_title>.*)\<\/title\>",
                            "STYLE":      r"\<link rel='stylesheet' type='text\/css' href='(?P<css_filename>.*)'\>\<\/link\>",
                            "JAVASCRIPT": r"\<script type='text\/javascript' src='(?P<js_filename>.*)'\>\<\/script\>"
                          }

            titleMatch  = re.compile( regExp["TITLE"] ).search( fileContent )
            if titleMatch:
                title = titleMatch.group( "page_title" )
            else:
                self._logger.error( "_parseIndexPage: no match for TITLE" )
                return ( None, None, None, None )

            codeJsMatch  = re.compile( regExp["JAVASCRIPT"] ).search( fileContent )
            if codeJsMatch:
                codeJsPath = glashartConfig.iptvBaseUrl + "/" + glashartConfig.tvmenuPath + "/" + codeJsMatch.group( "js_filename" )
            else:
                self._logger.error( "_parseIndexPage: no match for JAVASCRIPT" )
                return ( None, None, None, None )

            styleCssMatch  = re.compile( regExp["STYLE"] ).search( fileContent )
            if styleCssMatch:
                styleCssPath = glashartConfig.iptvBaseUrl + "/" + glashartConfig.tvmenuPath + "/" + styleCssMatch.group( "css_filename" )
            else:
                self._logger.error( "_parseIndexPage: no match for STYLE" )
                return ( None, None, None, None )

            return ( fileContent, title, codeJsPath, styleCssPath )
        else:
            return ( None, None, None, None )

    def _parseCodeJs( self, codeJsPath ):
        content, _, _ = getPage( codeJsPath )
        if content:
            fileHandle  = gzip.GzipFile( fileobj=StringIO( content ) )
            fileContent = fileHandle.read()
            parseOk     = True
            regExp = {
                        #                                   z                            [ b       ] ={ k                              :b          ,   c                                 :{ " default" :" Nederland 1" } ,   q                                  :{ " default" :" Nederland 1" } ,   j                            :" ned1" ,   m                            :" ned1" ,   s                              :" ned1.png" ,   t                              :" ned1.png" ,   o                              :" ned1.png" ,   n                                   :a          ,   d                               :[ ] ,   e                                 :[ ] } ;
                        "CHANNEL_LIST_1":                 r"(?P<channel_list>[A-Za-z]{1})\[[a-z]{1}\]=\{(?P<channel_number>[A-Za-z]{1}):[A-Za-z]{1},\s*(?P<channel_name_long>[A-Za-z]{1}):\{\"default\":\"Nederland 1\"\},\s*(?P<channel_name_short>[A-Za-z]{1}):\{\"default\":\"Nederland 1\"\},\s*(?P<channel_id_1>[A-Za-z]{1}):\"ned1\",\s*(?P<channel_id_2>[A-Za-z]{1}):\"ned1\",\s*(?P<channel_logo_1>[A-Za-z]{1}):\"ned1.png\",\s*(?P<channel_logo_2>[A-Za-z]{1}):\"ned1.png\",\s*(?P<channel_logo_3>[A-Za-z]{1}):\"ned1.png\",\s*(?P<prev_channel_number>[A-Za-z]{1}):[A-Za-z]{1},\s*(?P<channel_streams>[A-Za-z]{1}):\[\],\s*(?P<channel_unknown_1>[A-Za-z]{1}):\[\]\};",
                        #                                   a          ={ } ;   a          .e                             =" igmp:/ / 224     .1         .3         .1         :12110     " ;   a          .ta           =[{ia: "103"}];  a          .u          =1;   a          .D                              =1;
                        "CHANNEL_LIST_2":                 r"[A-Za-z]{1}=\{\};\s*[A-Za-z]{1}.(?P<channel_url>[A-Za-z]{1,2})=\"igmp:\/\/[0-9]{3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}\";\s*[A-Za-z]{1}.[A-Za-z]{1,2}=\[([^\]]*)\];\s*[A-Za-z]{1}.[A-Za-z]{1}=1;\s*[A-Za-z]{1}.(?P<channel_url_hd>[A-Za-z]{1})=1;",
                        #                                   for( $              .tv.l            .push( b            ) ;e            .length;) x                                 [ e            .pop( ) ] =b            ;
                        "CHANNEL_LIST_3":                 r"for\([\$A-Za-z]{1,2}.tv.[A-Za-z]{1,2}.push\([A-Za-z]{1,2}\);[A-Za-z]{1,2}.length;\)(?P<channel_id_list>[A-Za-z]{1,2})\[[A-Za-z]{1,2}.pop\(\)\]=[A-Za-z]{1,2};",
                        #                                   B                            [ b          ] ={ h                              :b          ,   a                                 :{ " default" :" Radio 3FM" } ,   m                                  :{ " default" :" Radio 3FM" } ,   g                            :" radio3" ,   j                            :" radio3" ,   p                              :" radio3fm.png" ,   q                              :" radio3fm.png" ,   n                              :" radio3fm.png" ,   s                             :1,   k                                   :a       ,c:[]   } ;
                        "CHANNEL_LIST_4":                 r"(?P<channel_list>[A-Za-z]{1})\[[A-Za-z]{1}\]=\{(?P<channel_number>[A-Za-z]{1}):[A-Za-z]{1},\s*(?P<channel_name_long>[A-Za-z]{1}):\{\"default\":\"Radio 3FM\"\},\s*(?P<channel_name_short>[A-Za-z]{1}):\{\"default\":\"Radio 3FM\"\},\s*(?P<channel_id_1>[A-Za-z]{1}):\"radio3\",\s*(?P<channel_id_2>[A-Za-z]{1}):\"radio3\",\s*(?P<channel_logo_1>[A-Za-z]{1}):\"radio3fm.png\",\s*(?P<channel_logo_2>[A-Za-z]{1}):\"radio3fm.png\",\s*(?P<channel_logo_3>[A-Za-z]{1}):\"radio3fm.png\",\s*(?P<channel_radio>[A-Za-z]{1}):1,\s*(?P<prev_channel_number>[A-Za-z]{1}):[a-z]{1}([^\}]+)\};",
                        #                                   Gb                                    =f          ;B          [ a          ] .i                                   =f          ;   for( B          [ f          ] .k          =a             ;e          .length;) w          [ e          .pop( ) ] =f          ;J          .root
                        "CHANNEL_LIST_5":                 r"(?P<last_channel_number>[A-Za-z]{1,2})=[A-Za-z]{1};[A-Za-z]{1}\[[A-Za-z]{1}\].(?P<next_channel_number>[A-Za-z]{1})=[A-Za-z]{1};\s*for\([A-Za-z]{1}\[[A-Za-z]{1}\].[A-Za-z]{1}=\s*[A-Za-z]{1};[A-Za-z]{1}.length;\)[A-Za-z]{1}\[[A-Za-z]{1}.pop\(\)\]=[A-Za-z]{1};[A-Za-z]{1}.root",
                        #                                   window.clearInterval( e            ) ;p                               ( fb           ) ;var c            =new r            ( o.Og                       ) ;c            .u            =d            ( ) ;s                               ( c            ) ;window.setTimeout( function( ) { ga           ( ) } ,50)
                        "PLAY_STREAM_ACTIONS":            r"window.clearInterval\([A-Za-z]{1,2}\);(?P<play_action_1>[A-Za-z]{1,2})\([A-Za-z]{1,2}\);var [A-Za-z]{1,2}=new [A-Za-z]{1,2}\([A-Za-z]{1,2}.[A-Za-z]{1,2}\);[A-Za-z]{1,2}.[A-Za-z]{1,2}=[A-Za-z]{1,2}\(\);(?P<play_action_2>[A-Za-z]{1,2})\([A-Za-z]{1,2}\);window.setTimeout\(function\(\)\{[A-Za-z]{1,2}\(\)\},50\)",
                        #                                   function Ce                                  ( a                                 ,b            ) {N            .call( this) ;if( b            ===undefined) b            =" " ;
                        "PLAY_STREAM_CLASS":              r"function (?P<play_stream_class>[A-Za-z]{1,2})\((?P<play_stream_url>[A-Za-z]{1,2}),[A-Za-z]{1,2}\){[A-Za-z]{1,2}.call\(this\);if\([A-Za-z]{1,2}===undefined\)[A-Za-z]{1,2}=\"\";",
                        "SET_CHANNEL_FUNCTION":           r"[A-Za-z]{1,2}.prototype.(?P<set_channel_function>[A-Za-z]{1,2})=function\([A-Za-z]{1,2},[A-Za-z]{1,2}\){if\(this.[A-Za-z]{1,2}\){window.clearTimeout\(this.[A-Za-z]{1,2}\);",
                        #                                   this.l            .appendChild( b            ) ;b            =new O            ( o            .fh           ) ;b            .ua           =function( ) {G                                      .ka(
                        "SET_CHANNEL_INSTANCE":           r"this.[A-Za-z]{1,2}.appendChild\([A-Za-z]{1,2}\);[A-Za-z]{1,2}=new [A-Za-z]{1,2}\([A-Za-z]{1,2}.[A-Za-z]{1,2}\);[A-Za-z]{1,2}.[A-Za-z]{1,2}=function\(\){(?P<set_channel_instance>[A-Za-z]{1,2}).%s\(",
                        "CHANNEL_OBJECT":                 r"(document.cookie=\"channel=\"\+encodeURIComponent\(this.(?P<channel_object_1>[A-Za-z]{1,2}).(?P<channel_object_2>[A-Za-z]{1,2})\);)",
                        "DEBUG_FUNCTION":                 r"function (?P<debug_function>[A-Za-z]{1,2})\([A-Za-z]{1,2}\){if\(window.console\)window.console.log\(",
                        "INIT_FUNCTION":                  r"for\(%s\(\"doRunAfterLoad\(\): \"\+[A-Za-z]{1,2}.length\);[A-Za-z]{1,2}.length;\)[A-Za-z]{1,2}.pop\(\)\(\)",
                        "LAST_JS_LINE":                   r"([A-Za-z]{1,2}\(\);\s*%s\(\"initial buildMenu\(\) done.\"\);)",
                        "KEY_EVENT_FUNCTION":             r"function (?P<key_event_function>[A-Za-z]{1,2})\([A-Za-z]{1,2}\)\{[A-Za-z]{1,2}\(\);[A-Za-z]{1,2}&&clearTimeout\([A-Za-z]{1,2}\);[A-Za-z]{1,2}=[A-Za-z]{1,2}.keyCode\|\|[A-Za-z]{1,2}.charCode;",
                     }
            symbolNames = {}
            symbolNames["channel_logo_path"]  = glashartConfig.channelLogoPath
            symbolNames["channel_thumb_path"] = glashartConfig.channelThumbPath

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

                # For the folloing matches I only need about 1500 characters starting from the start of this match
                channelListString = fileContent[channelList1Match.start():channelList1Match.start() + 1500]

                channelList2Match = re.compile( regExp["CHANNEL_LIST_2"] ).search( channelListString )
                if channelList2Match:
                    symbolNames["channel_url"]    = channelList2Match.group( "channel_url" )
                    symbolNames["channel_url_hd"] = channelList2Match.group( "channel_url_hd" )
                else:
                    self._logger.error( "_parseCodeJs: no match for CHANNEL_LIST_2" )
                    parseOk = False

                channelList3Match = re.compile( regExp["CHANNEL_LIST_3"] ).search( channelListString )
                if channelList3Match:
                    symbolNames["channel_id_list"] = channelList3Match.group( "channel_id_list" )
                else:
                    self._logger.error( "_parseCodeJs: no match for CHANNEL_LIST_3" )
                    parseOk = False

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
                        self._logger.error( "_parseCodeJs: mismatch in CHANNEL_LIST_4 with earlier matches!" )
                        parseOk = False
                else:
                    _logger.error( "_parseCodeJs: no match for CHANNEL_LIST_4" )
                    parseOk = False

                channelList5Match = re.compile( regExp["CHANNEL_LIST_5"] ).search( channelListString )
                if channelList5Match:
                    symbolNames["last_channel_number"] = channelList5Match.group( "last_channel_number" )
                    symbolNames["next_channel_number"] = channelList5Match.group( "next_channel_number" )
                else:
                    self._logger.error( "_parseCodeJs: no match for CHANNEL_LIST_5" )
                    parseOk = False
            else:
                self._logger.error( "_parseCodeJs: no match for CHANNEL_LIST_1" )
                parseOk = False

            playStreamActionsMatch = re.compile( regExp["PLAY_STREAM_ACTIONS"] ).search( fileContent )
            if playStreamActionsMatch:
                symbolNames["play_action_1"] = playStreamActionsMatch.group( "play_action_1" );
                symbolNames["play_action_2"] = playStreamActionsMatch.group( "play_action_2" );
            else:
                self._logger.error( "_parseCodeJs: no match for PLAY_STREAM_ACTIONS" )
                parseOk = False

            playStreamClassMatch = re.compile( regExp["PLAY_STREAM_CLASS"] ).search( fileContent )
            if playStreamClassMatch:
                symbolNames["play_stream_class"] = playStreamClassMatch.group( "play_stream_class" );
                symbolNames["play_stream_url"]   = playStreamClassMatch.group( "play_stream_url" );
            else:
                self._logger.error( "_parseCodeJs: no match for PLAY_STREAM_CLASS" )
                parseOk = False

            setChannelFunctionMatch = re.compile( regExp["SET_CHANNEL_FUNCTION"] ).search( fileContent )
            if setChannelFunctionMatch:
                symbolNames["set_channel_function"] = setChannelFunctionMatch.group( "set_channel_function" );
                setChannelInstanceMatch = re.compile( regExp["SET_CHANNEL_INSTANCE"] % ( symbolNames["set_channel_function"] ) ).search( fileContent )
                if setChannelInstanceMatch:
                    symbolNames["set_channel_instance"] = setChannelInstanceMatch.group( "set_channel_instance" );
                else:
                    self._logger.error( "_parseCodeJs: no match for SET_CHANNEL_FUNCTION" )
                    parseOk = False
            else:
                self._logger.error( "_parseCodeJs: no match for SET_CHANNEL_FUNCTION" )
                parseOk = False

            channelObjectMatch = re.compile( regExp["CHANNEL_OBJECT"] ).search( fileContent )
            if channelObjectMatch:
                symbolNames["channel_object_1"] = channelObjectMatch.group( "channel_object_1" );
                symbolNames["channel_object_2"] = channelObjectMatch.group( "channel_object_2" );
            else:
                self._logger.error( "_parseCodeJs: no match for CHANNEL_OBJECT" )
                parseOk = False

            debugFunctionMatch = re.compile( regExp["DEBUG_FUNCTION"] ).search( fileContent )
            if debugFunctionMatch:
                symbolNames["debug_function"] = debugFunctionMatch.group( "debug_function" );

                initFunctionMatch = re.compile( regExp["INIT_FUNCTION"] % ( symbolNames["debug_function"] ) ).search( fileContent )
                if not initFunctionMatch:
                    _logger.error( "_parseCodeJs: no match for INIT_FUNCTION" )
                    parseOk = False

                lastJSLineMatch = re.compile( regExp["LAST_JS_LINE"] % ( symbolNames["debug_function"] ) ).search( fileContent )
                if not lastJSLineMatch:
                    self._logger.error( "_parseCodeJs: no match for LAST_JS_LINE" )
                    parseOk = False
            else:
                self._logger.error( "_parseCodeJs: no match for DEBUG_FUNCTION" )
                parseOk = False

            keyEventFunctionMatch = re.compile( regExp["KEY_EVENT_FUNCTION"] ).search( fileContent )
            if keyEventFunctionMatch:
                symbolNames["key_event_function"] = keyEventFunctionMatch.group( "key_event_function" );
            else:
                _logger.error( "_parseCodeJs: no match for KEY_EVENT_FUNCTION" )
                parseOk = False

            if parseOk:
                return ( fileContent, symbolNames )
            else:
                return ( None, None )
        else:
            self._logger.error( "_parseCodeJs: no file content!" )
            return ( None, None )

    def _getStyleCss( self, styleCssPath ):
        content, _, _ = getPage( styleCssPath )
        if content:
            fileHandle  = gzip.GzipFile( fileobj=StringIO( content ) )
            fileContent = fileHandle.read()
            return fileContent
        return None

    def _modifyIndexPage( self, fileContent ):
        regExp      = {
                        "STYLE":              r"\<link rel='stylesheet' type='text\/css' href='(?P<css_filename>.*)'\>\<\/link\>",
                        "REPLACE_STYLE":      r"<link rel='stylesheet' type='text/css' href='style.css'></link>",
                        "JAVASCRIPT":         r"\<script type='text\/javascript' src='(?P<js_filename>.*)'\>\<\/script\>",
                        "REPLACE_JAVASCRIPT": r"<script type='text/javascript' src='api.js'/><script type='text/javascript' src='assets/js/service.js'/><script type='text/javascript' src='assets/js/stub.js'/><script type='text/javascript' src='assets/js/proxy.js'/><script type='text/javascript' src='code.js'></script>",
                      }
        # "REPLACE_STYLE"                     => "<link rel='stylesheet' type='text/css' href='style.css'></link>",
        # "REPLACE_JAVASCRIPT"                => "<script type='text/javascript' src='js/api.js'/><script type='text/javascript' src='js/service.js'/><script type='text/javascript' src='js/stub.js'/><script type='text/javascript' src='js/proxy.js'/><script type='text/javascript' src='code.js'></script>",

        fileContent, count = re.subn( regExp["STYLE"],
                                      regExp["REPLACE_STYLE"],
                                      fileContent )
        if count != 1:
            self._logger.error( "_modifyIndexPage: could not replace REPLACE_STYLE" )
            return None

        fileContent, count = re.subn( regExp["JAVASCRIPT"],
                                      regExp["REPLACE_JAVASCRIPT"],
                                      fileContent )
        if count != 1:
            self._logger.error( "_modifyIndexPage: could not replace REPLACE_JAVASCRIPT" )
            return None
        return fileContent

    def _modifyCodeJs( self, fileContent, symbolNames ):
        regExp = {
                    "CHANNEL_OBJECT":                 r"(document.cookie=\"channel=\"\+encodeURIComponent\(this.(?P<channel_object_1>[A-Za-z]{1,2}).(?P<channel_object_2>[A-Za-z]{1,2})\);)",
                    "REPLACE_SET_CHANNEL_FUNCTION":   r"\1/* id_begin */{var activeChannel = encodeURIComponent( this.%s.%s );window.setTimeout( function() { SetActiveChannel( encodeURIComponent( activeChannel ) ); }, 100 );}/* id_end */",
                    "LAST_JS_LINE":                   r"([A-Za-z]{1,2}\(\);\s*%s\(\"initial buildMenu\(\) done.\"\);)",
                    "REPLACE_LAST_JS_LINE":           r'/* id_begin */try { PowerOn(); } catch( e ) { %s( "Unable to call PowerOn(): " + e ); }/* id_end */\1',
                    "PLAY_STREAM_FUNCTION_PART_1":    r"(;function %s\([A-Za-z]{1,2},[A-Za-z]{1,2})",
                    "REPLACE_PLAY_STREAM_FUNCTION_1": r"\1/* id_begin */,localStream/* id_end */",
                    #                                   if( b          =this.fr           .exec( this.Ue           ) ) this.Ue           =" rtsp:/ / d-" + " abcdefghijklmnop" .charAt( uf           ( this,b            [ 1]) & 15) + " .zt6.nl/ " + b            [ 1] ;
                    "PLAY_STREAM_FUNCTION_PART_2":    r"(if\([A-Za-z]{1}=this.[A-Za-z]{1,2}.exec\(this.[A-Za-z]{1,2}\)\)this.[A-Za-z]{1,2}=\"rtsp:\/\/d-\"\+\"abcdefghijklmnop\".charAt\([A-Za-z]{1,2}\(this,[A-Za-z]{1,2}\[1\]\)&15\)\+\".zt6.nl\/\"\+[A-Za-z]{1,2}\[1\];)",
                    "REPLACE_PLAY_STREAM_FUNCTION_2": r"/* id_begin */if ( !localStream ){\1}/* id_end */",
                    "PROXY_OBJECT":                   r"(ASTB|PVR|AVMedia|Browser|VideoDisplay)\.",
                    "REPLACE_PROXY_OBJECT":           r"\1Proxy.",
                    #                                   if   ( b            =   a         .B           . redirect) {
                    "REDIRECT_FIX":                   r"if\s*\(([a-z]{1})\s*=\s*([a-z]{1}\.[A-Za-z]{1})\.redirect\){",
                    "REPLACE_REDIRECT_FIX":           r'if(\2.redirect){\1=\2.redirect;DebugLog( "Redirecting to: " + \1 );'
                 }
        #    "REPLACE_INIT_FUNCTION": "\${0};/* id_begin *//* id_end */",
        #    "REPLACE_LAST_JS_LINE": "/* id_begin */try { PowerOn(); } catch( e ) { %s( \"Unable to call PowerOn(): \" + e ); }/* id_end */\${0}",
        #    "REPLACE_SET_CHANNEL_FUNCTION": "\${0}/* id_begin */{var activeChannel = encodeURIComponent( this.%s.%s );window.setTimeout( function() { SetActiveChannel( encodeURIComponent( activeChannel ) ); }, 100 );}/* id_end */",
        #    "REPLACE_PLAY_STREAM_FUNCTION_1": "\${0}/* id_begin */,localStream/* id_end */",
        #    "REPLACE_PLAY_STREAM_FUNCTION_2": "/* id_begin */if ( !localStream ){\${0}}/* id_end */",
        #    "REPLACE_CHANNEL_LOCK": "\${1}0,",
        #    "REPLACE_PROXY_OBJECT": "\${1}Proxy.",
        #    "REPLACE_REDIRECT_FIX": "if(\${2}.redirect){\${1}=\${2}.redirect;DebugLog( \"Redirecting to: \" + \${1} );",

        fileContent, count = re.subn( regExp["LAST_JS_LINE"] % ( symbolNames["debug_function"] ),
                                      regExp["REPLACE_LAST_JS_LINE"] % ( symbolNames["debug_function"] ),
                                      fileContent )
        if count != 1:
            self._logger.error( "_modifyCodeJs: could not replace REPLACE_LAST_JS_LINE" )
            return None

        fileContent, count = re.subn( regExp["CHANNEL_OBJECT"],
                                      regExp["REPLACE_SET_CHANNEL_FUNCTION"] % ( symbolNames["channel_object_1"], symbolNames["channel_object_2"] ),
                                      fileContent )
        if count != 1:
            self._logger.error( "_modifyCodeJs: could not replace REPLACE_SET_CHANNEL_FUNCTION" )
            return None

        fileContent, count = re.subn( regExp["PLAY_STREAM_FUNCTION_PART_1"] % ( symbolNames["play_stream_class"] ),
                                      regExp["REPLACE_PLAY_STREAM_FUNCTION_1"],
                                      fileContent )
        if count != 1:
            self._logger.error( "_modifyCodeJs: could not replace REPLACE_PLAY_STREAM_FUNCTION_1" )
            return None

        fileContent, count = re.subn( regExp["PLAY_STREAM_FUNCTION_PART_2"],
                                      regExp["REPLACE_PLAY_STREAM_FUNCTION_2"],
                                      fileContent )
        if count != 1:
            self._logger.error( "_modifyCodeJs: could not replace REPLACE_PLAY_STREAM_FUNCTION_2" )
            return None

        fileContent, count = re.subn( regExp["PROXY_OBJECT"],
                                      regExp["REPLACE_PROXY_OBJECT"],
                                      fileContent )
        if count == 0:
            self._logger.error( "_modifyCodeJs: could not replace REPLACE_PROXY_OBJECT" )
            return None

        fileContent, count = re.subn( regExp["REDIRECT_FIX"],
                                      regExp["REPLACE_REDIRECT_FIX"],
                                      fileContent )
        if count != 1:
            self._logger.error( "_modifyCodeJs: could not replace REPLACE_REDIRECT_FIX" )
            return None

        return fileContent

    def _modifyApiJs( self, symbolNames ):
        apiFile = open( os.path.join( DATA_ROOT, "assets/js/api.js" ) )
        fileContent = apiFile.read()
        apiFile.close()

        if fileContent:
            fileContent = reduce( lambda x, y: x.replace( "{" + y + "}", symbolNames[y] ), symbolNames, fileContent )
            symbolMatch = re.findall( r'({[a-zA-Z0-9_]*})', fileContent )
            if len( symbolMatch ):
                self._logger.error( "_modifyApiJs: not all symbols replaced" )
                for match in symbolMatch:
                    self._logger.info( "_modifyApiJs: un-replaced symbol: %s", match )
                return None
            else:
                return fileContent
        else:
            return None
