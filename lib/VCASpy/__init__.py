#!/usr/bin/env python
#
# VCASpy a open source VCAS client
# Copyright (C) 2014 mielleman
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software 
# Foundation; either version 2 of the License, or (at your option) any later 
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with 
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple 
# Place, Suite 330, Boston, MA 02111-1307 USA
#
import logging

_haveVcas=True

try:
    import vcas.connector
except ImportError:
    _haveVcas = False

def VcasConnector( inputConfig, interface, outputJson, outputConstCw, macAddress ):
    global _haveVcas
    if _haveVcas:
        if macAddress == "":
            macAddress = None
        vcas.connector.Connector(input_config=inputConfig, interface=interface, output_json=outputJson, output_constcw=outputConstCw, mac=macAddress)
    else:
        logger = logging.getLogger( "VCASpy" )
        logger.error( "VCASpy not available!" )
