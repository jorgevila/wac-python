"""
        requestTokenUrl = 'https://pro1.api.wacapps.net/1/oauth/request-token'
        accessTokenUrl  = 'https://pro1.api.wacapps.net/1/oauth/access-token'
        authorizationUrl = 'https://pro1.api.wacapps.net/1/oauth/authorize'
        self.paymentUrl   = "https://pro1.api.wacapps.net/1/payment/acr:Authorization/transactions/amount"
        self.checktransactionUrl   = "https://pro1.api.wacapps.net/1/payment/acr:Authorization/transactions/amount/%s"
        self.listTransactionUrl   = "https://pro1.api.wacapps.net/1/payment/acr:Authorization/transactions/amount"
        self.discoveryUrl   = "http://pro1.api.wacapps.net/discovery/operator/%s"
        self.queryUrl = "https://pro1.api.wacapps.net/products/%s"
"""

requestTokenUrl='https://pro1.api.wacapps.net/1/oauth/request-token'
accessTokenUrl='https://pro1.api.wacapps.net/1/oauth/access-token'
authorizationUrl='https://pro1.api.wacapps.net/1/oauth/authorize'
paymentUrl="https://pro1.api.wacapps.net/1/payment/acr:Authorization/transactions/amount"
paymentCheckTransactionUrl   = "https://pro1.api.wacapps.net/1/payment/acr:Authorization/transactions/amount/%s"
paymentListTransactionUrl   = "https://pro1.api.wacapps.net/1/payment/acr:Authorization/transactions/amount"
discoveryUrl   = "https://pro1.api.wacapps.net/discovery/operator/%s"
queryUrl = "https://pro1.api.wacapps.net/products/%s"

baseStagingUrlHttpsR2 = "https://staging.api.wacapps.net/"
discoveryUrlR2   = "https://pro1.api.wacapps.net/discovery/operator/%s"
queryUrlR2 = "https://pro1.api.wacapps.net/products/%s"
authorizationStagingChargePathR2 = "https://pro1.api.wacapps.net/2/oauth/authorize";
accessTokenStagingChargePathR2 = "https://pro1.api.wacapps.net/2/oauth/access-token";
chargePaymentStagingPathR2 = "https://pro1.api.wacapps.net/2/payment/acr:Authorization/transactions/amount";
        
redirectUriOAuth='https://gateway.wacapps.net/redirect/9dc31536-026d-4c00-adf1-6957d80366da'

# oAuth Content Type 
oAuthContentType = 'application/x-www-form-urlencoded'
oAuthAccept = 'application/json'
SuccessPage = "https://res.api.wacapps.net/payment/confirm"
    
# oAuth scope
oAuthScopePay = 'POST-/payment/acr:Authorization/transactions/amount?code=%s'
oAuthScopeCheck = 'GET-/payment/acr:Authorization/transactions/amount'
oAuthScopeList = 'GET-/payment/acr:Authorization/transactions/amount'
    
oAuthdot2ScopePay = 'GET,POST-/payment/acr:Authorization/transactions/amount?code='
    
# oAuth Operator Mobile Network Code & Mobile Country Code 
oAuthOperatorMNC = None
oAuthOperatorMCC = None
oAuthOperatorName = None
    
# oAuth Consumer Key & Secret [Developer Credentials] 
oAuthConsumerKey = 'wac-3fcd2cbb8e806ef88311451818232a80d843af56' # Client ID
oAuthConsumerSecret = 'c48d214b98a0bc539b191076b61858f616fd3d25'  # Client secret
    
# Type of oAuth used by operator 
oauth_type = None
    
# oAuth Application settings [Application Details] 
oAuthAppID = 'wac-af76d90c-9ced-418b-a8d8-f6c45d0837a1'   # application ID
oAuthAppProductKey = None  # Item ID
oAuthAppUserName = 'developer1'
    
# User Application Callback 
app_callback = None
    
# WAC product query URL 
wacURLQueryProduct = None
    
#    WAC Product Information 
no_of_products = None
product_items = None
wacProductCurrency = None
wacProductPrice = None
wacProductDescription = None
wacProductBillingReceipt = None
    
#    WAC URLs for OAuth 1 flow 
oAuthURLRequestToken = None
oAuthURLAuthorizeToken = None
oAuthURLAccessToken = None
    
# WAC URLs for OAuth 2 flow 
oAuth2URLAuthorize = None
oAuth2URLAccessToken = None
    
#    WAC Payment URLs 
wacURLChargePayment = None
wacURLCheckTransaction = None
wacURLListTransactions = None
    
oauth_token=None
oauth_verifier=None
code=None
responseJSONForDot1 = None
    
oauth = None
token = None    

