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

var _searchRequestBusy          = false;

var __module = "aminopvr.webui.search";

function Search( queryString, where )
{
    var url = "/webui/search/?searchQuery=" + encodeURIComponent( queryString )
    if ( where )
    {
        url += "&where=" + encodeURIComponent( where );
    }
    window.location = url
}

function _updateSearch()
{
    if ( !_searchRequestBusy )
    {
        var searchQuery = $( '#search input[name="search"]' ).val();

        if ( searchQuery.length >= 3 )
        {
            _searchRequestBusy = true;

            var where = _getWhereFromSearchQuery( searchQuery );
            var query = _filterWhereFromSearchQuery( searchQuery );

            aminopvr.search( query, where, true, null, function( status, context, results ) { _updateSearchCallback( status, context, results ); }, true );
        }
        else if ( searchQuery.length == 0 )
        {
            _removeSearch();
        }
    }
}

function _getWhereFromSearchQuery( searchQuery )
{
    var supportedWhere = [ "programs", "channels", "recordings", "persons", "schedules" ];
    var words = searchQuery.split( ' ' );
    var where = [];
    for ( var word in words )
    {
        if ( words[word].toLowerCase().startsWith( "where:" ) )
        {
            whereClause = words[word].toLowerCase().split( ':' );
            if ( whereClause.length == 2 )
            {
                whereArray = whereClause[1].split( ',' );
                for ( var i in whereArray )
                {
                    if ( supportedWhere.indexOf( whereArray[i] ) == -1 )
                    {
                        logger.warning( __module, "_getWhereFromSearchQuery: where clause '" + whereArray[i] + "' not supported" );
                    }
                    else
                    {
                        where.push( whereArray[i] );
                    }
                }
            }
        }
    }

    if ( where.length == 0 )
    {
        where = supportedWhere;
    }

    return where.join( ',' );
}

function _filterWhereFromSearchQuery( searchQuery )
{
    var words = searchQuery.split( ' ' );
    var query = [];
    for ( var word in words )
    {
        if ( !words[word].toLowerCase().startsWith( "where:" ) )
        {
            query.push( words[word] );
        }
    }
    return query.join( ' ' );
}

function _removeSearch()
{
//    $( '#search_list' ).html( "" );
//    $( '#search_list' ).hide();
}

function _updateSearchCallback( status, context, results )
{
    var searchQuery = $( '#search input[name="search"]' ).val();

    if ( status && searchQuery.length > 0 )
    {
        try
        {
            var resultList = "";
            resultList += _fillSearchResults( results, "programs",   "Programs",   searchQuery );
            resultList += _fillSearchResults( results, "channels",   "Channels",   searchQuery );
            resultList += _fillSearchResults( results, "recordings", "Recordings", searchQuery );
            resultList += _fillSearchResults( results, "persons",    "Persons",    searchQuery );
            resultList += _fillSearchResults( results, "schedules",  "Schedules",  searchQuery );

            $( "#search_list" ).html( resultList );
            $( '#search_list' ).show();

            logger.info( __module, "_updateSearchCallback: Search results" );
        }
        catch ( e )
        {
            logger.error( __module, "_updateSearchCallback: exception: " + e );
        }
    }
    else if ( searchQuery.length == 0 )
    {
        _removeSearch();
    }

    _searchRequestBusy = false;
}

function _fillSearchResults( results, where, whereHuman, searchQuery )
{
    resultList = "";
    if ( where in results && results[where].length > 0 )
    {
        _sortSearchResults( results[where], searchQuery );

        resultList += "<ul><div>" + whereHuman + ":</div>";
        for ( var i = 0; i < Math.min( 5, results[where].length ); i++ )
        {
            resultList += "<li><a href=\"javascript:Search('" + results[where][i] + "', '" + where + "')\">" + results[where][i] + "</a><br /></li>";
        }
        resultList += "</ul>";
    }
    return resultList;
}

var _SEARCH_MATCH_WHOLE_STR         = 8
var _SEARCH_MATCH_BEGINNING_OF_STR  = 4
var _SEARCH_MATCH_WHOLE_WORD        = 2
var _SEARCH_MATCH_BEGINNING_OF_WORD = 1

function _determineMatchLevel( str, match )
{
    var level = 0;
    str   = str.toLowerCase();
    match = match.toLowerCase();
    if ( str == match )
    {
        level |= _SEARCH_MATCH_WHOLE_STR;
    }
    if ( str.startsWith( match ) )
    {
        level |= _SEARCH_MATCH_BEGINNING_OF_STR;
    }
    var words = str.split( /[\s;,\.]/ );
    for ( var word in words )
    {
        if ( words[word] == match )
        {
            level |= _SEARCH_MATCH_WHOLE_WORD;
        }
        if ( words[word].startsWith( match ) )
        {
            level |= _SEARCH_MATCH_BEGINNING_OF_WORD;
        }
    }
    return level;
}

function _sortSearchResults( results, searchQuery )
{
    // 1: match whole result
    // 2: match start of result
    // 3: match whole word in result
    // 4: match beginning of word in result
    // 5: everything else

    var matchLevel = {};
    function compare( a, b )
    {
        if ( !(a in matchLevel) )
        {
            matchLevel[a] = _determineMatchLevel( a, searchQuery );
        }
        if ( !(b in matchLevel) )
        {
            matchLevel[b] = _determineMatchLevel( b, searchQuery );
        }
        if ( matchLevel[a] > matchLevel[b] )
        {
            return -1;
        }
        else if ( matchLevel[a] < matchLevel[b] )
        {
            return 1;
        }
        return 0;
    }
    
    results.sort( compare );
}

$( function() {
    var search        = $( '#search' );
    var searchInput   = $( '<input>' ).attr( 'type', 'text' ).attr( 'name', 'search' ).attr( 'autocomplete', 'off' );
    var searchBox     = $( '<div>' ).addClass( 'search_box' ).append( searchInput );
    var searchOutline = $( '<div>' ).addClass( 'search_outline' ).append( searchBox );
    var searchList    = $( '<div>' ).attr( 'id', 'search_list' );
    search.append( searchOutline );
    search.append( searchList );

    searchInput.on( 'input', function( event ) { _updateSearch(); } );
    searchInput.focusout( function( event ) {
        setTimeout( function() {
            _removeSearch();
        }, 250 );
    } );

    searchInput.keydown( function(e) {
        var key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;
        if ( key == 13 )
        {
            e.preventDefault();

            var searchQuery = $( '#search input[name="search"]' ).val();
            var where       = _getWhereFromSearchQuery( searchQuery );
            var query       = _filterWhereFromSearchQuery( searchQuery );
            Search( query, where );
        }
    } );
} );
