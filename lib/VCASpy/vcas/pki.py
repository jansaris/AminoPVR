import hashlib
import M2Crypto
import os.path

from lib.VCASpy.vcas import Constants
#import vcas

MBSTRING_FLAG = 0x1000
MBSTRING_ASC  = MBSTRING_FLAG | 1
MBSTRING_BMP  = MBSTRING_FLAG | 2

class Certificates:
  def __init__(self, logger):
    self.logger = logger
    self.rsa = None
    self.pk = None

    self.csr = None 
    self.ca = None
    self.personal_cert = None
    self.personal_key_id = None

  def callback(self, *args):
    pass

  def CreatePrivateKey(self):
    self.rsa = M2Crypto.RSA.gen_key(bits=1024, e=3, callback=self.callback)
    self.pk = M2Crypto.EVP.PKey()
    self.pk.assign_rsa(self.rsa)

  def CreateCSR(self, company, email):
    self.csr = M2Crypto.X509.Request()

    name = self.csr.get_subject()
    name.C = Constants.APICountryName
    name.ST = Constants.APIStateOrProvinceName
    name.L = Constants.APILocalityName
    name.O = company
    name.OU = Constants.APIOrganizationalUnitName
    name.CN = Constants.APICommonName
    name.emailAddress = "%s/challengePassword=%s" % (email, Constants.APIChallengePassword)

    self.csr.set_subject_name(name)
    self.csr.set_pubkey(pkey=self.pk)
    self.csr.sign(pkey=self.pk, md='sha1')

  def loadCertificate(self, der):
    self.personal_cert = M2Crypto.X509.load_cert_string(der, M2Crypto.X509.FORMAT_DER)    
    self.personal_key_id = self.personal_cert.get_ext('subjectKeyIdentifier')
    return self.personal_key_id.get_value()

  def loadCACertificate(self, file):
    if not os.path.isfile(file):
      self.logger.error('Could not find the certificate file: %s' % file)
      exit(3)
    
    self.ca = M2Crypto.X509.load_cert(file, M2Crypto.X509.FORMAT_PEM)

  def getSignedHash(self, msg):
    md5 = hashlib.md5(msg).digest()
    signature = self.rsa.sign(md5, 'md5')
    hash = ''
    for b in signature:
      hash += '%02x' % ord(b)
    return hash
