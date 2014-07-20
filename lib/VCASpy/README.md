VCASpy
======
Verimatrix VCAS Python client. This script contact a VCAS VCI server, negotiates various variables and certificates after which it will try to contact a VCAS VKS server to retrieve the keys of all channels. The output is stored in a file.

## Requirements
Python 2.7.x (I have not tested with Python 3.x) and make sure you have the following Python modules in your Python include path:
- ssl
- json
- M2Crypto

## Usage
Form the commandline start the script:
```
./VCASpy.py -h
```
