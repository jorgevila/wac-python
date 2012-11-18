from fullscreenwrapper2 import *
import android
import os
import sys
import time
import waclib as wac
import simplejson
import pathhelpers

droid = android.Android()

class BuyScreen(Layout):
    
    rtKey = None
    rtSecret=None
    mcc = None
    mnc = None
    itemId=None
    
    def __init__(self,itemId,mcc,mnc):
        #initialize your class data attributes
        #load & set your xml
        self.mcc=mcc
        self.mnc=mnc
        self.itemId=itemId
        super(BuyScreen,self).__init__(pathhelpers.read_layout_xml("oauth.xml"),"WAC Showcase")

    def on_show(self):
        #initialize your layout views on screen_show
        self.start_authorization()
        
        #setup the event handlers for your layout views        
        self.views.br.add_event(click_EventHandler(self.views.br, self.browser_click))
        self.views.button.add_event(click_EventHandler(self.views.button, self.button_click))

    def browser_click(self,view,eventdata):
        myintent = droid.makeIntent('android.intent.action.VIEW', self.views.url.text, None, None).result 
        print myintent 
        droid.startActivityIntent(myintent) 
        
    def button_click(self,view,eventdata):        
        self.capture_verifier()
        
    def on_close(self):
        pass

    def capture_verifier(self):
        from urlparse import urlparse
        url = urlparse(self.views.verifier.text)
        params = dict([part.split('=') for part in url[4].split('&')])
        verifier = params['oauth_verifier']
        assert verifier != '' 
        status,atKey,atSecret = wacObj.fetch_access_token(verifier,self.rtKey,self.rtSecret,self.mcc,self.mnc)
        assert status == 200
        status,json_content = wacObj.issue_payment(atKey,atSecret)
        assert status == 200
        assert json_content != '' 

        payment_json=simplejson.loads(json_content)
        assert payment_json.has_key('amountTransaction') != ''
        txid=json_object["amountTransaction"]["serverReferenceCode"]
        FullScreenWrapper2App.get_android_instance().dialogCreateAlert("Confirmed payment:%s" % txid)
        FullScreenWrapper2App.get_android_instance().dialogSetPositiveButtonText("OK")
        FullScreenWrapper2App.get_android_instance().dialogShow()
        response=FullScreenWrapper2App.get_android_instance().dialogGetResponse().result
        FullScreenWrapper2App.get_android_instance().dialogDismiss()
        FullScreenWrapper2App.close_layout()
        
    def start_authorization(self):

        status,key,secret,authUrl=wacObj.fetch_payment_request_token(productId=self.itemId,callback=callback,mcc=self.mcc,mnc=self.mnc)
        self.rtKey=key
        self.rtSecret=secret
        #self.views.web.__setattr__('url',authUrl)
        self.views.url.text=authUrl
        

class ProductsScreen(Layout):
    
    json = None
    mcc = None
    mnc = None
    
    def __init__(self,mcc,mnc):
        #initialize your class data attributes
        #load & set your xml
        self.mcc=mcc
        self.mnc=mnc
        super(ProductsScreen,self).__init__(pathhelpers.read_layout_xml("main.xml"),"WAC Showcase")

    def on_show(self):
        #initialize your layout views on screen_show
        self.update_list()
        
        #setup the event handlers for your layout views        
        self.views.list.add_event(itemclick_EventHandler(self.views.list, self.item_click))
        
    def on_close(self):
        pass

    def item_click(self,view,eventdata):
        position = int(eventdata["data"]["position"])
        product=self.json["response"]["product"]["items"][int(position)]
        description="%s for %s %s" % (product['description'],product['price'],product['currency'])

        FullScreenWrapper2App.get_android_instance().dialogCreateAlert("Do you want to buy %s?" % description)
        FullScreenWrapper2App.get_android_instance().dialogSetPositiveButtonText("Yes")
        FullScreenWrapper2App.get_android_instance().dialogSetNegativeButtonText("No")
        FullScreenWrapper2App.get_android_instance().dialogShow()
        response=FullScreenWrapper2App.get_android_instance().dialogGetResponse().result
        FullScreenWrapper2App.get_android_instance().dialogDismiss()
        
        try:
            if response["which"]=="positive":
                itemId=product["item-id"]
                FullScreenWrapper2App.show_layout(BuyScreen(itemId,self.mcc,self.mnc))
        except:
            pass
        
        
    def close_out(self,view,event ):
        FullScreenWrapper2App.close_layout()
        
    def update_list(self):
        products =[]
#(200, '{"code":"ok","response":{"product":{"items":
#[{"item-id":"wac-c116480e-316a-44e7-be76-5fde978b2f59","description":"Discount Matinee","price":"0.01",
#"currency":"EUR","billing-receipt":"You purchased Discount Matinee for EUR .01. plus applicable tax."},
#{"item-id":"wac-11faf3e6-e440-4daa-824e-62d8ed83723e","description":"General Admission","price":"0.02",
#"currency":"EUR","billing-receipt":"You purchased General Admission for EUR .02. plus applicable tax."}],
#"application-id":"wac-939c6e89-f548-4811-a21c-84802cb242a8"}}}')

        status,json_content = wacObj.query_product(appId=wac_app_id,username=username,mcc=self.mcc,mnc=self.mnc)
        self.json=simplejson.loads(json_content)
        products_json=self.json["response"]["product"]["items"]
        for product in products_json:
                products.append("%s - %s %s" % (product['description'],product['price'],product['currency']))

        self.views.list.set_listitems(products)
    
class OpsScreen(Layout):
    
    json = None
    
    def __init__(self):
        #initialize your class data attributes
        #load & set your xml
        super(OpsScreen, self).__init__(pathhelpers.read_layout_xml("main.xml"),"WAC Showcase")

    def on_show(self):
        #initialize your layout views on screen_show
        self.update_list()
        
        #setup the event handlers for your layout views        
        self.views.list.add_event(itemclick_EventHandler(self.views.list, self.item_click))
        
    def on_close(self):
        pass

    def item_click(self,view,eventdata):
        position = int(eventdata["data"]["position"])
        # FullScreenWrapper2App.get_android_instance().dialogCreateAlert("Do you want to delete the meal - "+str(self.show_meals_list[position]))
        # FullScreenWrapper2App.get_android_instance().dialogSetPositiveButtonText("Yes")
        # FullScreenWrapper2App.get_android_instance().dialogSetNegativeButtonText("No")
        # FullScreenWrapper2App.get_android_instance().dialogShow()
        # response=FullScreenWrapper2App.get_android_instance().dialogGetResponse().result
        # FullScreenWrapper2App.get_android_instance().dialogDismiss()
        operators=self.json["response"]["operators"]
        mcc=operators[int(position)]["mcc"]
        mnc=operators[int(position)]["mnc"]        
        FullScreenWrapper2App.show_layout(ProductsScreen(mcc,mnc))
        
    def close_out(self,view,event ):
        FullScreenWrapper2App.close_layout()
        
    def update_list(self):
        listOps =[]
        #(200, '{"code":"ok","response":{"operators":[{"name":"Kt","mcc":"450","mnc":"08"},
        #{"name":"Telekom DE","mcc":"262","mnc":"01"},{"name":"Movistar ES","mcc":"214","mnc":"07"}
        #,{"name":"SK Telecom","mcc":"450","mnc":"05"},{"name":"SMART","mcc":"515","mnc":"03"},
        #{"name":"LG U+","mcc":"450","mnc":"06"}]}}')

        status,json_content = wacObj.discover_operator(wac_app_id)
        self.json=simplejson.loads(json_content)
        operators=self.json["response"]["operators"]
        for op in operators:
            listOps.append(op['name'])

        self.views.list.set_listitems(listOps)

#########################
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
        
wacObj = wac.WACOneAPIPayment(my3leggedConsumer, my3leggedSecret)

if __name__ == '__main__':    
    
    droid = android.Android()
    FullScreenWrapper2App.initialize(droid)
    FullScreenWrapper2App.show_layout(OpsScreen())
    FullScreenWrapper2App.eventloop()
