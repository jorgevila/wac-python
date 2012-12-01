# 
# The MIT license
#
# Copyright (C) 2012 by Jorge Vila ( @jorgevila )
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import oauth2 as oauth
import httplib2, pickle, os, types, time, urllib, simplejson, uuid
import wac_constants
from types import *
from urlparse import parse_qs
from datetime import datetime

__author__ = '@jorgevila'
__license__  = 'MIT'
__version__  = '1.0'

# # # # # # # # # # # # # # # # 
# OAuth base Class
# # # # # # # # # # # # # # # #

class WACOAuth():
    """
    Version: 1.0
    OAuth Support for WAC SDK interaction
    """

    consumer = None
    realm = None
    version = None
    debugFlag = False
    
    http = httplib2.Http()

    """
    Methods for the oAuth Dance.
    It supports Out Of Band authorization as defined in oAuth 1.0a 
    """ 
    def __init__(self, consumerKey, consumerSecret,realm=None):
        """
        @param consumerKey: (string):     Key of the Consumer 
        @param consumerSecret: (string):  Secret of the Consumer        
        """
        
        self.realm = realm
        self.consumer = oauth.Consumer(consumerKey, consumerSecret)
    
    def _signAndSend(self, requestUrl, method, token, parameters={}, body="", \
                     extraHeaders={}, is_form_encoded = False):
        """
        Generic method to call an oAuth authorized API including oAuth signature.
        
        @param requestUrl: (string):       The BlueVia URL
        @param method: (string):           HTTP method, "GET" or "POST"
        @param token: (oauth.Token):       Usually the Access Token. During oAuth Dance None or Request Token
        @param parameters: (dict):         Necessary call paramters, e.g. version, alt. Default: None
        @param body: (string):             Body of the HTTP call. Default: ""
        @param extraHeaders: (dict):       Some calls need extra headers, e.g. {"Content-Type":wac_constants.oAuthAccept}. Default: None
        @param is_form_encoded: (boolean): If True parameters are send as form encoded HTTP body. DEFAULT: False
        @return: (tuple):                  (HTTP response, HTTP response data)
        """
        
        req = oauth.Request.from_consumer_and_token(self.consumer, token, method, requestUrl, \
                                                    parameters, body, is_form_encoded)
        req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), self.consumer, token)

        if self.debugFlag:
            print "Consumer: %s" % self.consumer
            print "Token: %s" % token
            print "signature = %s" % req['oauth_signature']
            print "signature_method = %s" % req['oauth_signature_method']

        headers = self.to_header(req, realm=self.realm)
#        headers = req.to_header(realm=self.realm)
        if parameters.has_key("xoauth_apiName"):
            headers['Authorization'] += ', xoauth_apiName="%s"' % parameters.get("xoauth_apiName")
            
        if extraHeaders:
            headers.update(extraHeaders)

        header_keys = headers.keys()
        header_keys.sort()
        sorted_header={}
        for keyitem_header in header_keys:
            sorted_header[keyitem_header]=headers[keyitem_header]

        headers = sorted_header

        if is_form_encoded:
            # get version and alt parameter only
            params = [p for p in parameters.items() if p[0] in ["version","alt"]]
        else:
            # remove oauth_ parameters like oauth_callback
            params = [p for p in parameters.items() if p and p[0][:6] != "oauth_"]

        query = None
        if params:
            query = "&".join(["%s=%s" % (p[0], p[1]) for p in params])
            if query:
                requestUrl += "?" + query

        if self.debugFlag: self._debug(requestUrl, query, headers, body, token, req)

        if self.debugFlag:
            print "Before request: %s" % datetime.now()
        response, content = self.http.request(requestUrl, method, body, headers)
        if self.debugFlag:
            print "After request: %s" % datetime.now()

        if self.debugFlag:
            print('response["status"] = %s' % response["status"])
            print('content =\n %s' % content)
            
        return response, content

    def to_header(self, req, realm=''):
        """Serialize as a header for an HTTPAuth request."""
        oauth_params = ((k, v) for k, v in req.items() 
                            if k.startswith('oauth_'))
        stringy_params = ((k, oauth.escape(str(v))) for k, v in oauth_params)
        header_params = ('%s="%s"' % (k, v) for k, v in stringy_params)
        params_header = ', '.join(header_params)
 
        auth_header = 'OAuth'
        if realm != '':
            auth_header = '%s realm="%s"' % (auth_header,realm)
            if params_header:
                auth_header = "%s, %s" % (auth_header, params_header)
        else:
            if params_header:
                auth_header = "%s %s" % (auth_header, params_header)
 
        return {'Authorization': auth_header}

    def set_debug(self, dbgFlag):
        """
        Set or unset the debug flag
        @param dbgFlag: (boolean): If True debug information will be printed to stdout
        """
        
        self.debugFlag = dbgFlag
    

    def _debug(self, requestUrl, query, headers, body, token, req):
        """
        Prints aut anything relevant for oAuth debugging: URL, method, body, headers, signature base string, ...
        @note: Internal method
        """

        print "%s" % datetime.now()
        print("\nurl   = " + requestUrl)
        if not query: query = ""
        print("\nquery = " + query)
        print("\nhead  = " + simplejson.dumps(headers, indent = 2).replace(", ", ",\n"))
        try:
            bstr = simplejson.dumps(simplejson.loads(body), indent = 2)
        except:
            bstr = body
        print("\nbody  = " + bstr)
        if req != None:
            sm =  oauth.SignatureMethod_HMAC_SHA1()
            key, base = sm.signing_base(req, self.consumer, token)
            print("\noAuth signature components")
            print("\nbase  = " + base)
            print("\nkey   = " + key)


    def fetch_request_token(self, parameters, extraHeaders, requestTokenUrl=None, authorizationUrl=None):
        """
        Request the Request Token for the OAuth Dance
        
        @param callback: (string): The callback URL or "oob". Default: "oob"
        @return: (tuple):           (HTTP status, token key, authorization URL). HTTP status == "200" for success
        """
        assert type(requestTokenUrl) is StringType and requestTokenUrl!= "", "'requestTokenUrl' must be a non empty string"
        assert type(authorizationUrl) is StringType and authorizationUrl!= "", "'authorizationUrl' must be a non empty string"
        if requestTokenUrl == None:
            requestTokenUrl=wac_constants.requestTokenUrl
        if authorizationUrl == None:
            authorizationUrl=wac_constants.authorizationUrl
                    
        response, content = self._signAndSend(requestTokenUrl, "POST", None, \
                                              parameters=parameters, \
                                              body="", is_form_encoded=True, \
                                              extraHeaders=extraHeaders)
        if response["status"] == '200':
            request_token = oauth.Token.from_string(content)
            return int(response["status"]), request_token.key, request_token.secret,"%s?oauth_token=%s" % (authorizationUrl, request_token.key)
        else:
            return int(response["status"]), content
    
    def fetch_wac_request_token(self, scope="", mcc="", mnc="", callback=None, requestTokenUrl=None, authorizationUrl=None):
        """
        First call of the OAuth dance for WAC request token

        @param scope: (string):      Scope in the WAC Form
        @param mcc: (string):      MCC
        @param mnc: (string):      MNC
        @param callback: (string):    The callback URL to receive verifier at
        @param requestTokenURL: (string):    URL for the request Token first call on WAC
        @param authorizationURL: (string):   URL for authorization redirection

        @return: (tuple):             (HTTP status, token_key, token_secret, authorization URL). HTTP status == "200" for success
        """
        assert type(scope) is StringType and scope!= "", "'scope' must be a non empty string"
        assert type(mcc) is StringType and mcc!= "", "'mcc' must be a non empty string"
        assert type(mnc) is StringType and mnc!= "", "'mnc' must be a non empty string"        
        assert type(requestTokenUrl) is StringType and requestTokenUrl!= "", "'requestTokenUrl' must be a non empty string"
        assert type(authorizationUrl) is StringType and authorizationUrl!= "", "'authorizationUrl' must be a non empty string"
        if requestTokenUrl == None:
            requestTokenUrl=wac_constants.requestTokenUrl
        if authorizationUrl == None:
            authorizationUrl=wac_constants.authorizationUrl
            
        #extra_headers={"Content-Type":"wac_constants.oAuthContentType;charset=UTF8","x-mnc":mnc,"x-mcc":mcc}
        extra_headers={"x-mnc":mnc,"x-mcc":mcc}                     
        parameters={"oauth_scope":scope,"oauth_callback":callback}

        status,key,secret,authUrl=self.fetch_request_token(parameters, extra_headers,requestTokenUrl=requestTokenUrl, authorizationUrl=authorizationUrl)
        return status,key,secret,authUrl+"&x-mcc=%s&x-mnc=%s" % (mcc,mnc)

    def fetch_accessToken(self, verifier, request_token, request_token_secret, mcc, mnc,  accessTokenUrl=None):
        """
        The final step of the oAuth Dance. Exchange the Request Token for the Access Token after getting the verifier
        
        @param verifier: (string): The oAuth verifier of the successful user authorization
        @param request_token: (string): Request Token key
        @param request_token_secret: (string): Request Token secret
        @param mcc: (string): MCC
        @param mnc: (string): MNC
        @param accessTokenUrl: (string): Access token URL on WAC service
        
        @return: (string):         HTTP status == "200" for success
        """
        assert request_token != None, "Oauth 'request_token' must be non empty"
        assert request_token_secret != None, "Oauth 'request_token_secret' must be non empty"
        assert type(verifier) is StringType and verifier!= "", "Oauth 'verifier' must be a non empty string"
        assert type(mcc) is StringType and mcc!= "", "'mcc' must be a non empty string"
        assert type(mnc) is StringType and mnc!= "", "'mnc' must be a non empty string" 
        assert type(accessTokenUrl) is StringType and accessTokenUrl!= "", "'authorizationUrl' must be a non empty string"
        if accessTokenUrl == None:
            accessTokenUrl=wac_constants.accessTokenUrl
            
        request_token = oauth.Token.from_string("oauth_token=%s&oauth_token_secret=%s" % (request_token,request_token_secret))
        request_token.set_verifier(verifier)
        
        response, content = self._signAndSend(accessTokenUrl, "POST", request_token, 
                                              parameters={},body="",is_form_encoded=True,
                                              extraHeaders={"x-mnc":self.mnc,"x-mcc":self.mcc})
        if response["status"] == '200':
            access_token = oauth.Token.from_string(content)
            return int(response["status"]),access_token.key, access_token.secret,
        else:
            return int(response["status"]), content
    
# # # # # # # # # # # # # # # # 
# OneAPI Payment Class
# # # # # # # # # # # # # # # # 
class WACOneAPIPayment(WACOAuth):
    """
    The WAC class supporting class for payments for OAuth 1.0a for OneAPI through WAC
    """
    mcc=None
    mnc=None

    def __init__(self, consumerKey, consumerSecret, realm = "", version="v1",mcc=None,mnc=None):
        """
        Initialize the WAC OneAPI Payment object

        @param consumerKey: (string):     Key of the Consumer 
        @param consumerSecret: (string):  Secret of the Consumer 
        @param realm: (string):   Realm string; Defaults: "BlueVia"
        @param version: (string): Defaults "v1"
        @param mcc: (string): MCC. Defaults "None"
        @param mnc: (string): MNC. Defaults "None"
        """
        
        WACOAuth.__init__(self, consumerKey, consumerSecret, realm="")
        self.realm = realm
        self.version = version
        self.mcc=mcc
        self.mnc=mnc             

    def fetch_payment_request_token(self, productId="", mcc=None,mnc=None, callback=None):
        """
        First call of the oAuth Dance to get a token valid for Payment.
        Payment API requires POST scope

        @param productId: (string):      Price in the form 125 for 1.25
        @param mcc: (string): MCC. Defaults "None"
        @param mnc: (string): MNC. Defaults "None"
        @param callback: (string):    The callback URL or "oob". Default: "oob"

        @return: (tuple):             (HTTP status, token_key, token_secret, authorization URL). HTTP status == "200" for success
        """
        assert type(productId) is StringType and productId!= "", "'productId' must be a non empty string"
        if mcc != None:
            self.mcc=mcc
        if mnc != None:
            self.mnc=mnc
        scope= wac_constants.oAuthScopePay % productId            

        return self.fetch_wac_request_token(scope, self.mcc, self.mnc, callback, wac_constants.requestTokenUrl, wac_constants.authorizationUrl)


    def fetch_information_request_token(self, callback=None):
        """
        First call of the oAuth Dance to get a token valid to get information on payments.
        Scope requires GET

        @param callback: (string):    The callback URL or "oob". Default: "oob"

        @return: (tuple):             (HTTP status, token_key, token_secret, authorization URL). HTTP status == "200" for success
        """
        scope=wac_constants.oAuthScopeCheck     
        return self.fetch_wac_request_token(scope, self.mcc, self.mnc, callback, wac_constants.requestTokenUrl, wac_constants.authorizationUrl)

    def discover_operator(self, appId, apiName='',mcc="",mnc=""):
        """
        Discover operator API

        URL: http://api.wacapps.net/discovery/operator/{application-id}/{api-name}/

        @param appId: (string):    WAC Application ID
        @param apiName: (string):    API name
        @param mcc: (string):    MCC
        @param mnc: (string):    MNC

        @return: (tuple):             (HTTP status, HTTP Content). HTTP status == "200" for success
        """
        
        assert type(appId) is StringType and appId!= "", "'appId' must be a non empty string"
        assert type(mcc) is StringType, "'mcc' must be a string"
        assert type(mnc) is StringType, "'mnc' must be a string"        
        
        method="GET"
        headers={}
        body=""
        url=wac_constants.discoveryUrl % appId
        if apiName != "":
            url = "%s/%s" % (url,apiName)

        params={}
        if mnc != "" and mcc != "":
            params={"x-mnc":mnc,"x-mcc":mcc}

        query = None
        if params:
            query = "&".join(["%s=%s" % (p[0], p[1]) for p in params])
            if query:
                url += "?" + query
        
        if self.debugFlag:
            print "%s %s" % (method,url)

        response, content = self.http.request(url, method, body, headers)
        
        if self.debugFlag:
            print('response["status"] = %s' % response["status"])
            print('content =\n %s' % content)
            
        return int(response["status"]), content            

    def query_product(self, appId, username, mcc="",mnc="", productId=""):
        """
        QUery Product API

        URL: http://api.wacapps.net/discovery/operator/{application-id}/{api-name}/

        @param appId: (string):    WAC Application ID
        @param username: (string):    User name
        @param mcc: (string):    MCC
        @param mnc: (string):    MNC
        @param productId: (string):    Product Id

        @return: (tuple):             (HTTP status, HTTP Content). HTTP status == "200" for success
        """
        
        assert type(appId) is StringType and appId!= "", "'appId' must be a non empty string"
        assert type(mcc) is StringType and mcc!= "", "'mcc' must be a non empty string"
        assert type(mnc) is StringType and mnc!= "", "'mnc' must be a non empty string"        
        assert type(productId) is StringType, "'productId' must be a string"        
        assert type(username) is StringType, "'username' must be a non empty string"        

        url=wac_constants.queryUrl % appId
        if productId != "":
            url = "%s/%s" % (url,productId)

        extra_headers={"x-mnc":mnc,"x-mcc":mcc}            
        method="GET"
        timestamp="%s000" % int(time.time())
        params={"client_id":self.consumer.key,"timestamp":timestamp}
        body=""
        query = None
        if params:
            query = "&".join(["%s=%s" % (p[0], p[1]) for p in params.items()])
            if query:
                url += "?" + query

#        req = oauth.Request(method, url,extra_headers)
#        req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), self.consumer, None)
        import hmac
        import hashlib
        import base64
        if self.debugFlag:
            print "Secret: %s" % self.consumer.secret
            print "MSG: %s%s" % (username,appId)
        hashed = hmac.new (self.consumer.secret, msg='%s%s%s' % (username,appId,timestamp), digestmod=hashlib.sha256).digest()
        base64_hash=base64.b64encode(hashed)
        signature=base64_hash.encode("hex")
        
        headers =  extra_headers

        headers['Authorization']="%s" % signature
    
        if self.debugFlag: self._debug(url, query, headers, body, None, None)

        response, content = self.http.request(url, method, body, headers)
        
        return int(response["status"]), content

    def issue_payment(self, accessTokenKey=None, accessTokenSecret=None, referenceCode=None):   
        """
        Issue the actual payment with details from given by fetch_request_token method
        @param accessTokenKey: (string):    Access Token for payment
        @param accessTokenSecret: (string):    Access token secret for payment
        @param referenceCode: (string):    Payment reference code

        @return: (tuple):              (HTTP status, (dict) paymentStatus). HTTP status == "200" for success.          
        """
        assert type(self.mcc) is StringType and self.mcc!= "", "'mcc' must be a non empty string"
        assert type(self.mnc) is StringType and self.mnc!= "", "'mnc' must be a non empty string"
        assert self.consumer != None, "load oAuth credentials"
        assert type(accessTokenKey) is StringType and accessTokenKey!= "", "'accessTokenKey' must be a non empty string"
        assert type(accessTokenSecret) is StringType and accessTokenSecret!= "", "'accessTokenSecret' must be a non empty string" 
        accessToken=oauth.Token.from_string("oauth_token=%s&oauth_token_secret=%s" % (accessTokenKey,accessTokenSecret))
        assert self.accessToken != None, "'accessToken' must not be empty"

        if referenceCode == None:
            referenceCode = str(uuid.uuid4().hex)

        '''
        endUserId= acr:Authorization&
        transactionOperationStatus=Charged&
        description= Single%20general%20admission%20theater%20ticket& 
        code=wac-11faf3e6-e440-4daa-824e-62d8ed83723e&
        referenceCode=REF-ASM600-239238&
        onBehalfOf=WAC%20Cinemas%20Inc& 
        purchaseCategoryCode=Ticket& 
        channel=WAP&
        productID=wac-c88382a1-4a21-48ef-a67c-959b8eb05950
        '''
        paymentInfo = {"endUserId":"acr:Authorization", "transactionOperationStatus":"Charged",
                       "description":"test description","code":self.productId,"referenceCode":referenceCode}
        extra={"x-mnc":self.mnc,"x-mcc":self.mcc,"Accept":wac_constants.oAuthAccept,"Content-Type":wac_constants.oAuthContentType}
        
        body = urllib.urlencode(paymentInfo)
        body = body.replace("+", "%20")

        params=parse_qs(body)
        response, content = self._signAndSend(self.paymentUrl, "POST", self.accessToken, \
                                              parameters=params, body=body, \
                                              extraHeaders=extra,is_form_encoded = True)
        return int(response["status"]), content
                

    def check_payment(self, transactionId, accessTokenKey=None, accessTokenSecret=None):
        """
        Check the Payment status (polling)
        
        @param transactionId: (string): Transaction Id provided by issuePayment method
        @param accessTokenKey: (string):    Access Token for payment
        @param accessTokenSecret: (string):    Access token secret for payment

        @return: (tuple):              (HTTP status, (dict) paymentStatus). HTTP status == "200" for success.          
        """
        assert self.consumer != None, "load oAuth credentials"
        assert type(accessTokenKey) is StringType and accessTokenKey!= "", "'accessTokenKey' must be a non empty string"
        assert type(accessTokenSecret) is StringType and accessTokenSecret!= "", "'accessTokenSecret' must be a non empty string" 
        accessToken=oauth.Token.from_string("oauth_token=%s&oauth_token_secret=%s" % (accessTokenKey,accessTokenSecret))
        assert self.accessToken != None, "'accessToken' must not be empty"
        assert type(transactionId) is StringType and transactionId!= "", "'transactionId' must be a non empty string"
        assert type(self.mcc) is StringType and self.mcc!= "", "'mcc' must be a non empty string"
        assert type(self.mnc) is StringType and self.mnc!= "", "'mnc' must be a non empty string" 

        body = ""
        extra={"x-mnc":self.mnc,"x-mcc":self.mcc,"Accept":wac_constants.oAuthAccept}
        response, content = self._signAndSend(wac_constants.paymentCheckTransactionUrl % transactionId, 
                                              "GET", accessToken, \
                                              parameters={}, body="", is_form_encoded=True,\
                                              extraHeaders=extra)

        return int(response["status"]), content 

    def list_transactions(self, accessTokenKey=None, accessTokenSecret=None):   
        """
        List Transactions associated to token
        @param accessTokenKey: (string):    Access Token for payment
        @param accessTokenSecret: (string):    Access token secret for payment

        @return: (tuple):              (HTTP status, (dict) paymentStatus). HTTP status == "200" for success.          
        """
        assert self.consumer != None, "load oAuth credentials"
        assert type(accessTokenKey) is StringType and accessTokenKey!= "", "'accessTokenKey' must be a non empty string"
        assert type(accessTokenSecret) is StringType and accessTokenSecret!= "", "'accessTokenSecret' must be a non empty string" 
        accessToken=oauth.Token.from_string("oauth_token=%s&oauth_token_secret=%s" % (accessTokenKey,accessTokenSecret))
        assert self.accessToken != None, "'accessToken' must not be empty"
             
        response, content = self._signAndSend(wac_constants.paymentListTransactionUrl, "GET", accessToken, \
                                              parameters={}, body="", \
                                              extraHeaders={"x-mnc":self.mnc,"x-mcc":self.mcc,"Accept":wac_constants.oAuthAccept})
        return int(response["status"]), content
