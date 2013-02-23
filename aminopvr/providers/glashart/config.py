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
from aminopvr.config import ConfigSectionAbstract
import aminopvr

class GlashartConfig( ConfigSectionAbstract ):
    _section = "Glashart"
    _options = {
                 "iptv_base_url":       "http://w.zt6.nl",
                 "tvmenu_path":         "%(iptv_base_url)s/tvmenu",
                 "tvmenu_index_path":   "%(iptv_base_url)s/tvmenu/index.xhtml.gz",
                 "tvmenu_code_js_path": "%(iptv_base_url)s/tvmenu/code.js.gz",
                 "epg_data_path":       "%(iptv_base_url)s/epgdata",
                 "epg_channels_path":   "%(iptv_base_url)s/epgdata/channels",
                 "channel_logo_path":   "%(iptv_base_url)s/images/channels",
                 "grab_epg_time":       "06:00",
                 "grab_epg_interval":   "24h"
               }

    @property
    def iptvBaseUrl( self ):
        return self._get( "iptv_base_url" )

    @property
    def tvmenuPath( self ):
        return self._get( "tvmenu_path" )

    @property
    def tvmenuIndexPath( self ):
        return self._get( "tvmenu_index_path" )

    @property
    def tvmenuCodeJsPath( self ):
        return self._get( "tvmenu_code_js_path" )

    @property
    def epgDataPath( self ):
        return self._get( "epg_data_path" )

    @property
    def epgChannelsPath( self ):
        return self._get( "epg_channels_path" )

    @property
    def channelLogoPath( self ):
        return self._get( "channel_logo_path" )

    @property
    def grabEpgTime( self ):
        return self._get( "grab_epg_time" )

    @property
    def grabEpgInterval( self ):
        return self._get( "grab_epg_interval" )

glashartConfig = GlashartConfig( aminopvr.config )
