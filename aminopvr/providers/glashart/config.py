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
from aminopvr.config import ConfigSectionAbstract, defaultConfig

class GlashartConfig( ConfigSectionAbstract ):
    _section = "Glashart"
    _options = {
                 "iptv_base_url":           "http://w.stb.zt6.nl",
                 "tvmenu_path":             "tvmenu",
                 "tvmenu_index_path":       "%(iptv_base_url)s/%(tvmenu_path)s/index.xhtml.gz",
                 "epg_data_path":           "%(iptv_base_url)s/epgdata",
                 "epg_channels_path":       "%(iptv_base_url)s/epgdata/channels",
                 "channel_logo_path":       "%(iptv_base_url)s/%(tvmenu_path)s/images/channels",
                 "channel_thumb_path":      "%(iptv_base_url)s/%(tvmenu_path)s/images/channelsthumb",
                 "grab_epg_time":           "06:00",
                 "grab_epg_interval":       "24h",
                 "grab_content_time":       "06:00",
                 "grab_content_interval":   "24h",
                 "vcas_update_interval":    "7d",
                 "vcas_ini_file":           "../iptv/Verimatrix.ini",
#                 "vcas_interface":          "eth1",
#                 "vcas_json_file":          "../iptv/channels.json",
#                 "vcas_const_cw_file":      "../iptv/constcw",
#                 "vcas_mac_address":        "001122334455"
               }

defaultConfig.append( GlashartConfig )
