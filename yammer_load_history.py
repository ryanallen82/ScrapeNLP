#!/usr/bin/env python

import oauth2 as oauth
import time
import urlparse
import pyodbc
import webbrowser as web


try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

TOKEN_STORE = "yammer.token"

#OAuth details for SENewsPosterBot
#Consumer (Application) Key
CONSUMER_KEY = 'A42XoZTpezB1jMzVaiSKw'

#Consumer (Application) Secret
CONSUMER_SECRET = 'nPOQXwdUrToovO3QlSLvrOEDjW8n33aFhN69mAxlA'

#Request Token URL
REQUEST_TOKEN_URL = 'https://www.yammer.com/oauth/request_token'

#Access Token URL
ACCESS_TOKEN_URL = 'https://www.yammer.com/oauth/access_token'

#Authorize URL
AUTH_URL = 'https://www.yammer.com/oauth/authorize'

authKey = ''
authSecret = ''

source = 'Yammer'

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

# this can be either xml or json
url = 'https://www.yammer.com/api/v1/messages.xml'

token = oauth.Token(key=authKey, secret=authSecret)
consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)

client = oauth.Client(consumer, token)
resp, content = client.request(url)

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=R0224576\RYANSQLSERVER;DATABASE=FAQ;UID=m097654;Trusted_Connection=yes')
cursor = cnxn.cursor()

i = 0
while i < 100:
	mina = cursor.execute("select coalesce(min(ID),0) from Stage_FACT").fetchone()[0]
	if mina == 0:
		url = 'https://www.yammer.com/api/v1/messages/my_feed.xml'
	else:
		url = 'https://www.yammer.com/api/v1/messages/my_feed.xml?older_than='+str(mina)

	resp,content = client.request(url, 'GET')

	with open('yammer.xml','w') as f:
		f.write(content)
		f.close()
		tree = ET.parse('yammer.xml')
		for elem in tree.iter(tag='messages'):
			for n in elem:
				for nm in n:
					group = 'None'
					if nm.tag == 'id':
						ID = nm.text
					elif nm.tag == 'sender-id':
						send = nm.text
					elif nm.tag == 'web-url':
						web = nm.text
					elif nm.tag == 'body':
						for x in nm:	
							if x.tag == 'plain':
								if x.text == None:
									msg = 'None'
								else:
									msg = x.text
					elif nm.tag == 'thread-id':
						thread = nm.text
					elif nm.tag == 'created-at':
						created = nm.text
						
				cursor.execute('insert into Stage_FACT(Thread_ID,ID,msg,sender_id,created_at,data_source) values (?,?,?,?,?,?)',thread,ID,msg,send,created,source)
				cursor.execute('insert into Stage_dim_msgs(Thread_ID,web_url) values(?,?)',thread,web)
				cnxn.commit()


		print "Lowest ID: ", mina


	i+=1
	print 'Iteration #: ',i
	time.sleep(3)









