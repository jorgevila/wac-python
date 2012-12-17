### GET CONF
import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read("test.properties")
section="main"

my3leggedConsumer = Config.get(section, 'my3leggedConsumer')
my3leggedSecret = Config.get(section, 'my3leggedSecret')

wac_app_id=Config.get(section, 'wac_app_id')
productId = Config.get(section, 'productId')
callback = Config.get(section, 'callback')
mcc=Config.get(section, 'mcc')
mnc=Config.get(section, 'mnc')
username=Config.get(section, 'username')


### Logging

import sys
class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

sys.stdout = Logger("payment.log")

### PAYMENT 

import waclib as wac
from datetime import datetime

print "%s" % datetime.now()

def next():
    text = raw_input('\nPress Enter to continue...')
    return 0;

print 'Launching...'
o3 = wac.WACOneAPIPayment(my3leggedConsumer, my3leggedSecret)
o3.set_debug(True)

#print ' Discover Operator'

#print o3.discover_operator(wac_app_id)

#next()

#print ' Query Products'

#print o3.query_product(appId=wac_app_id,username=username,mcc=mcc,mnc=mnc)

#next()

#print ' Query Product %s' % productId

#print o3.query_product(appId=wac_app_id,username=username,mcc=mcc,mnc=mnc,productId=productId)

#next()


print 'Request token...'
status,token,secret,content=o3.fetch_payment_request_token(productId=productId,callback=callback,mcc=mcc,mnc=mnc)
print "\nSTATUS: %s \n CONTENT: %s" % (status,content)
assert status == 200
auth_url_with_token=content
print "PARAMS from RT:\n token_key=%s \ntoken_secret=%s \n auth_url= %s" % (token,secret,auth_url_with_token)
assert status == 200

#Authorizing token


import urllib2
import urllib

mcc_mnc=urllib.urlencode({"x-mnc":mnc,"x-mcc":mcc})
auth_url_with_token_and_mcc="%s&%s" % (auth_url_with_token,mcc_mnc)
#print auth_url_with_token_and_mcc

next()
print ".... authorize token.."

#urlBV_with_verifier = raw_input('\nPaste URL obtained from authorization flow and press Enter:')

#from urlparse import urlparse
#url = urlparse(urlBV_with_verifier)
#params = dict([part.split('=') for part in url[4].split('&')])
#print params
#verifier = params['oauth_verifier']

verifier = raw_input('\nPaste verifier:')

next()

print "Get Access Token..."
# When finished copy verifier, e.g 135791
status,accesstoken,accesssecret,content = o3.fetch_access_token( verifier, token, secret, mcc, mnc, accessTokenUrl=None)
assert status == 200
next()

print "\nPayment...\n"
status,json_content = o3.issue_payment(accesstoken,accesssecret)
print "\nSTATUS: %s \n CONTENT: %s" % (status,json_content)
assert status == 201
assert json_content != '' 
next()

import simplejson
json_object=simplejson.loads(json_content)
assert json_object.has_key('amountTransaction') != ''
txid=json_object["amountTransaction"]["serverReferenceCode"]
txId_url=json_object["amountTransaction"]["resourceURL"]

print "\n\nCheck Payment with Payment Access Token\n\n"
status,json_content = o3.check_payment(txid,accesstoken,accesssecret)
print "\nSTATUS: %s \n CONTENT: %s" % (status,json_content)
assert status == 200
