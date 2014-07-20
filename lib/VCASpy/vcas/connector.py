#!/usr/bin/env python

import fcntl
import socket
import struct
import json
import ConfigParser
import logging
import os.path

from lib.VCASpy.vcas import api
#import vcas
#import vcas.api

class Connector:

  def __init__(self, input_config, interface, output_json, output_constcw, mac=None):
    self.input_config = input_config
    self.interface = interface
    self.output_json = output_json
    self.output_constcw = output_constcw

    #logging.basicConfig()
    self.logger = logging.getLogger('VCASpy')
    #self.logger.setLevel(logging.INFO)

    self.config = {}
    self.parseConfig()

    if mac == None:
      mac = self.getMAC(interface)

    # setup our API
    self.api = api.API(logger=self.logger, mac=mac, config=self.config)

    self.api.createSessionKey()
    self.api.getCertificate()
    self.api.getAllChannelKeys()

    # write the keys to a dump file
    if self.output_json:
      self.logger.info('Saving all channel data as JSON to: %s' % output_json)

      f = open(self.output_json, 'w')
      json.dump(obj=self.api.keys, fp=f)
      f.close()

    # write the binary data
    if self.output_constcw:
      self.logger.info('Saving all channel data as constcw to: %s' % output_constcw)

      f = open(self.output_constcw, 'w')
      f.write(self.api.constcw)
      f.close()

  def getMAC(self, interface):
    self.logger.info('Trying to determine the MAC address of interface: %s' % interface)

    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', interface[:15]))
      mac = ''.join(['%02x' % ord(char) for char in info[18:24]]).upper()
    except IOError:
      self.logger.error('The supplied interface could not be found.')
      exit(2)

    self.logger.debug('getMAC: return %s' % mac)
    return mac

  def parseConfig(self, section='VERIMATRIX'):
    self.logger.info('Reading configuration from: %s, expecting section: %s to be populated.' % (self.input_config, section))

    if not os.path.isfile(self.input_config):
      self.logger.error('Could not find the configuration file: %s' % self.input_config)
      exit(4)

    try:
      cp = ConfigParser.ConfigParser()
      cp.read(self.input_config)
      for option in cp.options(section):
        self.logger.debug('parseConfig: Found %s: %s' % (option, cp.get(section, option)))
        self.config[option] = cp.get(section, option)
    except ConfigParser.NoSectionError:
      self.logger.error('Could not find the section %s in the configuration file %s' % (section, self.input_config))
      exit(5)

    vks_serveraddress, vks_serverport = self.config['preferred_vks'].split('/', 2)
    self.config['vks_serveraddress'] = vks_serveraddress
    self.config['vks_serverport'] = int(vks_serverport)

    self.logger.debug('parseConfig: Parsed %s: %s' % ("vks_serveraddress", vks_serveraddress))
    self.logger.debug('parseConfig: Parsed %s: %s' % ("vks_serverport", vks_serverport))
