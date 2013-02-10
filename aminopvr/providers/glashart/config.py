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
