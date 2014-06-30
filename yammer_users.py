#!/usr/bin/env python

import oauth2 as oauth
import time
import urlparse
import pyodbc
import webbrowser as web
import sys
import yammer_settings

try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET


TOKEN_STORE = "yammer.token"

#OAuth details for SENewsPosterBot
#Consumer (Application) Key
CONSUMER_KEY, CONSUMER_SECRET = yammer_settings.keys() 
server = yammer_settings.server()

#Request Token URL
REQUEST_TOKEN_URL = 'https://www.yammer.com/oauth/request_token'

#Access Token URL
ACCESS_TOKEN_URL = 'https://www.yammer.com/oauth/access_token'

#Authorize URL
AUTH_URL = 'https://www.yammer.com/oauth/authorize'

authKey = ''
authSecret = ''

source = 'Yammer'
sender_id = 'None'
state = None
active_date = None
name = None
timezone = None
email = None


if (authKey == ''):
    consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    client = oauth.Client(consumer)

    resp, content = client.request(REQUEST_TOKEN_URL, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))

    url = "%s?oauth_token=%s" % (AUTH_URL, request_token['oauth_token'])
    web.open_new_tab(url)


    oauth_verifier = raw_input('What is the PIN? ')

    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(ACCESS_TOKEN_URL, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    print "Access Token:"
    print "access token = %s" % access_token['oauth_token']
    print "access secret = %s" % access_token['oauth_token_secret']
    print
    print "You may now access protected resources using the access tokens above." 
    print

    toStore = access_token['oauth_token'] + "\n", access_token['oauth_token_secret'] + "\n"
    authKey = access_token['oauth_token']
    authSecret = access_token['oauth_token_secret']    
    file_object = open(TOKEN_STORE, 'w')
    file_object.writelines (toStore)
    file_object.close( )

token = oauth.Token(key=authKey, secret=authSecret)
consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)

client = oauth.Client(consumer, token)
resp, content = client.request(url)


cnxn = pyodbc.connect(server)
cursor = cnxn.cursor()

i = 365
while i < 1000:
	url = 'https://www.yammer.com/api/v1/users.xml?page='+str(i)

	resp,content = client.request(url, 'GET')

	with open('user.xml','w') as f:
		f.write(content)
		f.close()
		tree = ET.parse('user.xml')
		for elem in tree.iter(tag='response'):
			for nm in elem:
				if nm.tag == 'id':
					sender_id = nm.text
				elif nm.tag == 'state':
					state = nm.text
				elif nm.tag == 'full-name':
					name = nm.text
				elif nm.tag == 'activated-at':
					active_date = nm.text	
				elif nm.tag == 'contact':
					for x in nm:	
						if x.tag == 'email-addresses':
							for y in x:
								if y.tag == 'email-address':
									for b in y:
										if b.tag == 'address':
											email = b.text
				elif nm.tag == 'timezone':
					timezone = nm.text

			cursor.execute('''insert into dim_users_stage(sender_id,state,active_date,name,timezone,email,data_source) values (?,?,?,?,?,?,?)''',
				sender_id,state,active_date,name,timezone,email,source)
				
			cnxn.commit()
			print name," added."
	print i
	i += 1	
	time.sleep(3)