#!/usr/bin/env python

import string
import random
import time
import socket
import struct
import ssl
import base64
import inspect
import pprint
import M2Crypto
import logging

#import vcas
#import vcas.pki
from lib.VCASpy.vcas import pki
from lib.VCASpy.vcas import Constants

class API:

  # this will create a LOT of debug files
  # only use when needed ;)
  DEBUG = False

  def __init__(self, logger, mac, config):
    self.logger = logger
    self.mac = mac
    self.config = config

    self.client_id = self.generateClientID()
    self.email_address = self.generateEmailAddress()

    # our goal is to fill this dict and blob
    self.keys = {}
    self.constcw = None

    # setup our keys and certificates
    self.pki = pki.Certificates(self.logger)
    self.pki.CreatePrivateKey()
    self.pki.CreateCSR(self.config['company'], self.email_address)
    self.pki.loadCACertificate(self.config['rootcert'])

    self.session_key = None
    self.session_aes_key = None
    self.session_key_string = None
    self.subject_key_id = None

  def debug(self, filename, data):
    if not self.DEBUG:
      return False
    f = open('debug.' + filename, 'w')
    f.write(data)
    return f.close()

  def getCertificate(self):
    cmd = self.buildCMD(
      self.client_id,
      Constants.APIGetCertificate,
      self.config['company'],
      Constants.APINa,
      Constants.APINa,
      self.pki.csr.as_pem(),
      Constants.APICommonName,
      Constants.APIAddress,
      Constants.APIEmptyArgument,
      Constants.APILocalityName,
      Constants.APIStateOrProvinceName,
      Constants.APIZipCode,
      Constants.APICountryName,
      Constants.APITelephoneNumber,
      self.email_address,
      self.mac,
      Constants.APIChallengePassword)

    # |____4___|_____4_______|_____________|
    # |_length_|_cert_length_|_Certificate_|
    # 0000000: 0000 0424 2004 0000 3082 041c 3082 0385  ...$ ...0...0...
    # 0000010: a003 0201 0202 0478 1d0c e330 0d06 092a  .......x...0...*
    # 0000020: 8648 86f7 0d01 0104 0500 3081 9d31 0b30  .H........0..1.0
    # etc
    data = self.sendVCI(cmd)
    self.subject_key_id = self.pki.loadCertificate(data[8:]).replace(':', '')

    # debugging specific
    self.logger.info('Retrieved the VCI signed certificate and extracted my subject key ID: %s' % self.subject_key_id)
    self.debug('getCertificate.signed.der', data[8:])
    self.debug('getCertificate.csr.pem', self.pki.csr.as_pem())
    self.debug('getCertificate.subject_key_id', self.subject_key_id)

  def createSessionKey(self):
    # MessageFormat~UniqueClientID~CreateSessionKey~Company~$MAC~
    api = self.buildCMD(
      self.client_id,
      Constants.APICreateSessionKey,
      self.config['company'],
      self.mac)

    # |___16____|_____19____|____6____|
    # |_AES key_|_TimeStamp_|_Unknown_|
    # 0000000: fea3 900d 459d 24e8 6eee e7e0 7720 1d8c  ....E.$.n...w ..
    # 0000010: 3037 2f30 372f 3230 3134 2032 313a 3031  07/07/2014 21:01
    # 0000020: 3a35 3000 0000 0000 00                   :50......
    self.session_key = self.sendVCI(api)
    self.session_aes_key = ''.join(self.session_key[:16])
    self.session_timestamp = ''.join(self.session_key[16:35])

    # debugging specific
    self.logger.info('Retrieved the VCI session timestamp: %s and AES key: %s' % (self.session_timestamp, self.session_aes_key.encode('hex').upper()))
    self.debug('createSessionKey.session_key', self.session_key)
    self.debug('createSessionKey.session_aes_key', self.session_aes_key)
    self.debug('createSessionKey.session_timestamp', self.session_timestamp)

  def getAllChannelKeys(self):
    # build the API command
    api = self.buildCMD(
      self.config['company'],
      self.session_timestamp,
      self.mac,
      self.client_id,
      Constants.APIGetAllChannelKeys,
      self.config['company'],
      self.subject_key_id,
      self.pki.getSignedHash(self.session_timestamp),
      self.mac,
      Constants.APIEmptyArgument,
      Constants.APIEmptyArgument)

    # send the command and expect data
    self.constcw = self.sendVKS(api)

    if not self.constcw:
      print 'getAllChannelKeys() ERROR'
      exit(2)
    
    # determine the number of channels in our response
    total_channels = struct.unpack('<l', self.constcw[:4])[0]

    self.logger.info('Retrieved the VKS channels, found %d channels in total' % total_channels)

    # iterate and unpack each 108 bytes
    for id in range(1,total_channels+1):
      start = 4 + ((id-1)*108)
      raw = self.constcw[start:start+108]
      number = struct.unpack('<l', raw[:4])[0]

      self.keys[number] = {
        "id": id,
        "keys": {
          1: {
            "key":      raw[4:20].encode('hex'),
            "start":    "%4d-%02d-%02d %02d:%02d:%02d" % struct.unpack('<hhhhhh', raw[20:32]),
            "stop":     "%4d-%02d-%02d %02d:%02d:%02d" % struct.unpack('<hhhhhh', raw[36:48]),
            "duration": struct.unpack('<L', raw[52:56])[0]
          },
          2: {
            "key":      raw[56:72].encode('hex'),
            "start":    "%4d-%02d-%02d %02d:%02d:%02d" % struct.unpack('<hhhhhh', raw[72:84]),
            "stop":     "%4d-%02d-%02d %02d:%02d:%02d" % struct.unpack('<hhhhhh', raw[88:100]),
            "duration": struct.unpack('<L', raw[104:108])[0]
            }
          }
        }

  def sendVKS(self, cmd):
    caller = inspect.stack()[1][3]
    header = self.buildCMD(
      self.config['company'],
      self.session_timestamp,
      self.mac)

    self.debug("sendVKS.%s.cmd" % caller, cmd)

    cmd = cmd.replace(header, "", 1)

    rc4 = M2Crypto.RC4.RC4()
    rc4.set_key(self.session_aes_key)
    encrypted = rc4.update(cmd)

    payload = ''.join([header, encrypted])

    # tcp socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.config['vks_serveraddress'], self.config['vks_serverport'] + 1))
    s.sendall(payload)

    data = []
    while True:
      buffer = s.recv(8192)
      if not buffer:
        break
      data.append(buffer)

    data = ''.join(data)

    rc4 = M2Crypto.RC4.RC4()
    rc4.set_key(self.session_aes_key)
    decrypted = rc4.update(data[4:])

    self.debug("sendVKS.%s.socket" % caller, repr(s.getpeername()))
    self.debug("sendVKS.%s.payload" % caller, payload)
    self.debug("sendVKS.%s.data" % caller, data)
    self.debug("sendVKS.%s.decrypted" % caller, decrypted)

    s.close()

    return decrypted

  def sendVCI(self, cmd):
    caller = inspect.stack()[1][3]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(s)

    ssl_sock.connect((self.config['serveraddress'], int(self.config['serverport'])))
    ssl_sock.write( unicode(cmd, "utf-8") )

    msg_size = struct.unpack('>l', ssl_sock.recv(4))[0]
    data = ssl_sock.recv(msg_size - 4)

    self.debug("sendVCI.%s.socket" % caller, "%s\n%s\n%s\n" 
	                                       % (repr(ssl_sock.getpeername()), 
						  ssl_sock.cipher(), 
						  pprint.pformat(ssl_sock.getpeercert())))
    self.debug("sendVCI.%s.cmd" % caller, cmd)
    self.debug("sendVCI.%s.data" % caller, data)

    ssl_sock.close()

    return data

  def buildCMD(self, *args):
    api = self.config['message_format'] +''+ Constants.APISeparator
    for value in args:
      api += '%s%s' % (value, Constants.APISeparator)

    self.logger.debug('buildCMD: %s' % api)
    return api

  def generateEmailAddress(self):
    email = '%s.%d@Verimatrix.com' % (self.mac, int(time.time()));
    self.logger.debug('generateEmailAddress: %s' % email)
    return email

  def generateClientID(self, size=28, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    id = ''
    for _ in range(size):
      id += '%2X' % ord(random.choice(chars))
    self.logger.debug('generateClientID: %s' % id)
    return id
