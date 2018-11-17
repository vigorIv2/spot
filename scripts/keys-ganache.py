#!/usr/bin/env python
import json
from pprint import pprint
import sys
file = sys.argv[1]
print file
json_data=open(file).read()
data = json.loads(json_data)
for a in data['addresses']:
    pubkeyArray=data['addresses'][a]['publicKey']['data']
    pubkey=""
    for pbk in pubkeyArray:
        pubkey = "%s%02x" % (pubkey,pbk)
    print "Address:%s" % a
    print "Public Key:0x%s" % pubkey 
    print "Private Key:0x%s" % data['private_keys'][a]
