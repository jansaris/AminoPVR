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
from aminopvr.const import DATA_ROOT
import ConfigParser
import logging
import os


class ConfigSectionAbstract( object ):
    _section = None
    _options = {}
    _logger  = logging.getLogger( "aminopvr.ConfigSectionAbstract" )

    def __init__( self, config ):
        assert self._section != None, "_section member not defined!"
        assert self._options != None, "_options not defined!"

        self._logger.debug( "ConfigSectionAbstract<%s>.__init__( config=%r )" % ( self._section, config ) )

        self._config         = config
        self._sectionOptions = self._config.getSection( self._section )
        if not self._sectionOptions:
            self._logger.warning( "ConfigSectionAbstract<%s>.__init__: section doesn't exist, so added" )
            self._config.addSection( self._section )

        unsupportedOptions = set( self._sectionOptions ).difference( set( self._options.keys() ) )
        for option in unsupportedOptions:
            self._logger.warning( "ConfigSectionAbstract<%s>.__init__: option: %s not supported" % ( self._section, option ) )

    def _get( self, option ):
        assert self._section != None, "_section member not defined!"
        assert self._options != None and self._options.has_key( option ), "_options not defined or _options[%s] doesn't exist!" % ( option )
        self._addIfNew( option )
        return self._config.get( self._section, option )

    def _getint( self, option ):
        assert self._section != None, "_section member not defined!"
        assert self._options != None and self._options.has_key( option ), "_options not defined or _options[%s] doesn't exist!" % ( option )
        self._addIfNew( option )
        return self._config.getInt( self._section, option )

    def _getfloat( self, option ):
        assert self._section != None, "_section member not defined!"
        assert self._options != None and self._options.has_key( option ), "_options not defined or _options[%s] doesn't exist!" % ( option )
        self._addIfNew( option )
        return self._config.getFloat( self._section, option )

    def _getboolean( self, option ):
        assert self._section != None, "_section member not defined!"
        assert self._options != None and self._options.has_key( option ), "_options not defined or _options[%s] doesn't exist!" % ( option )
        self._addIfNew( option )
        return self._config.getBoolean( self._section, option )

    def _addIfNew( self, option ):
        assert self._section != None, "_section member not defined!"
        assert self._options != None and self._options.has_key( option ), "_options not defined or _options[%s] doesn't exist!" % ( option )
        if option not in self._sectionOptions:
            self._config.set( self._section, option, str( self._options.has_key( option ) ) )

    def _set( self, option, value ):
        assert self._section != None, "_section member not defined!"
        assert self._options != None and self._options.has_key( option ), "_options not defined or _options[%s] doesn't exist!" % ( option )
        self._config.set( self._section, option, str( value ) )

class GeneralConfig( ConfigSectionAbstract ):
    _section = "General"
    _options = {
                 "api_key":              "",
                 "server_port":          "8080",
                 "provider":             "Glashart",
                 "input_stream_support": "multicast,http",
                 "local_access_nets":    "127.0.0.1"
               }

    """
    TODO: on initialization check apiKey. If it doesn't exist or it is not strong enough, generate one.
    """

    @property
    def apiKey( self ):
        return self._get( "api_key" )

    @property
    def serverPort( self ):
        return self._get( "server_port" )

    @property
    def provider( self ):
        return self._get( "provider" )

    @property
    def inputStreamSupport( self ):
        return self._get( "input_stream_support" )

    @property
    def localAccessNets( self ):
        return self._get( "local_access_nets" ).split( ',' )

class Config( object ):
    _instance = None

    _logger   = logging.getLogger( "aminopvr.Config" )

    def __new__( self, *args, **kwargs ):
        if not self._instance:
            self._instance = super( Config, self ).__new__( self, *args, **kwargs )
        return self._instance

    def __init__( self, filename="aminopvr.conf"  ):
        self._logger.debug( "Config.__init__( filename=%s )" % ( filename ) )
        self._filename = filename
        self._config   = ConfigParser.ConfigParser()
        self._config.read( Config.configFilename( self._filename ) )

    def getSection( self, section ):
        options = None
        if self._config.has_section( section ):
            options = self._config.options( section )
        return options

    def addSection( self, section ):
        if self._config.has_section( section ):
            self._config.add_section( section )

    def get( self, section, option ):
        return self._config.get( section, option )

    def getInt( self, section, option ):
        return self._config.getint( section, option )

    def getFloat( self, section, option ):
        return self._config.getfloat( section, option )

    def getBoolean( self, section, option ):
        return self._config.getboolean( section, option )

    def set( self, section, option, value ):
        self._config.set( section, option, str( value ) )

    @staticmethod
    def configFilename( filename ):
        return os.path.join( DATA_ROOT, filename )

config = Config()
