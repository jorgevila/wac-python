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
msisdn=Config.get(section, 'msisdn')
password=Config.get(section, 'password')

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


print ' Discover Operator'

print o3.discover_operator(wac_app_id)

next()

print ' Query Products'

print o3.query_product(appId=wac_app_id,username=username,mcc=mcc,mnc=mnc)

next()

print ' Query Product %s' % productId

print o3.query_product(appId=wac_app_id,username=username,mcc=mcc,mnc=mnc,productId=productId)

next()


print 'Request token...'
status,content=o3.fetch_payment_request_token(productId=productId,callback=callback,mcc=mcc,mnc=mnc)
print "\nSTATUS: %s \n CONTENT: %s" % (status,content)
assert status == 200
auth_url_with_token=content
print "PARAMS from RT:\n token_key=%s \ntoken_secret=%s \n auth_url= %s" % (o3.request_token.key, o3.request_token.secret,auth_url_with_token)
assert status == 200

next()
#Authorizing token


import urllib2
import urllib

mcc_mnc=urllib.urlencode({"x-mnc":mnc,"x-mcc":mcc})
auth_url_with_token_and_mcc="%s&%s" % (auth_url_with_token,mcc_mnc)
print auth_url_with_token_and_mcc

next()

print ".... authorize token.."

urlBV_with_verifier = raw_input('\nPaste URL obtained from authorization flow and press Enter:')

from urlparse import urlparse
url = urlparse(urlBV_with_verifier)
params = dict([part.split('=') for part in url[4].split('&')])
print params
verifier = params['oauth_verifier']

next()

print "Get Access Token..."
# When finished copy verifier, e.g 135791
status,content = o3.fetch_access_token(verifier)
assert status == 200
next()

# When finished copy verifier, e.g 135791
status,content=o3.fetch_info_access_token(verifier)
print "\nSTATUS: %s \n CONTENT: %s" % (status,content)
assert status == 200
next()

import simplejson
json_object=simplejson.loads(json_content)
assert json_object.has_key('amountTransaction') != ''
txid=json_object["amountTransaction"]["serverReferenceCode"]
txId_url=json_object["amountTransaction"]["resourceURL"]

print "\n\nCheck Payment with Payment Access Token\n\n"
status,json_content = o3.check_payment(txid)
print "\nSTATUS: %s \n CONTENT: %s" % (status,json_content)
assert status == 200

print "\n\nList transactions\n"
status,json_content = o3.list_transactions()
print "\nSTATUS: %s \n CONTENT: %s" % (status,json_content)
assert status == 200
next()

print "\n\nList transactions for %s\n\n\n" % content
assert json_content != '' 
import simplejson
json_object=simplejson.loads(json_content)
assert json_object.has_key('paymentTransactionList')
assert json_object['paymentTransactionList'].has_key('amountTransaction') != ''

transactionsList=json_object['paymentTransactionList']['amountTransaction']

for transaction in transactionsList:
    txid=transaction["serverReferenceCode"]
    txId_url=transaction["resourceURL"]
    print "\n%s %s" % (txId_url,txid) 