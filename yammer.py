import pyodbc
import oauth2 as oauth
import time
import urlparse
import webbrowser as web
import sys
import yammer_settings

server = yammer_settings.server()
CONSUMER_KEY, CONSUMER_SECRET = yammer_settings.keys()
try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

class YammerFact:

	def __init__(self):
		cnxn, cursor, maxid = self.database_connect()
		self.fact(cnxn, cursor, maxid)
		self.dim_msg(cnxn, cursor)

	def database_connect(self):
		cnxn = pyodbc.connect(server)
		cursor = cnxn.cursor()

		maxid = cursor.execute("select coalesce(max(ID),0) from FACT").fetchone()[0]
		print maxid
		return (cnxn, cursor, maxid)


	def fact(self, cnxn, cursor, maxid):
		cursor.execute('select * from Stage_FACT where ID > ?', maxid)
		rows = cursor.fetchall()


		kws = ['sharepoint','excel','powerpivot', 'powerquery','power pivot', 'power query', 
		'performancepoint', 'sql server', 'ssas', 'ssrs', 'msbi', 'ssis','sp']

		i = 0
		for row in rows:
			for k in kws:
				if k in row[2].lower().split():
					print k, ' in ', row[0], ' added'
					cursor.execute('insert into Stage_Clean_FACT select distinct * FROM Stage_FACT WHERE Thread_ID = ?',row[0])
					i += 1
				cnxn.commit()
		print i," rows transferred"

		cursor.execute('insert into FACT select distinct * from Stage_Clean_FACT where ID > ?', maxid)

	def dim_msg(self, cnxn, cursor):	
		cursor.execute('delete from dim_msgs')
		cursor.execute('''INSERT INTO  [dbo].[dim_msgs] SELECT *
		  FROM (
		                SELECT  *, 
		                        ROW_NUMBER() OVER(PARTITION BY [Thread_ID] ORDER BY [Thread_ID]) rn
		                    FROM [dbo].[Stage_dim_msgs]
		              ) a
		WHERE rn = 1 ''')
		cnxn.commit()

class YammerLoad:

	def __int__(self):
		client = self.connect_yammer()
		cnxn, cursor = self.database_connect()
		self.get_yammer_data(cursor,cnxn,client)

	def connect_yammer(self,TOKEN_STORE = "yammer.token", CONSUMER_KEY = 'A42XoZTpezB1jMzVaiSKw', 
		CONSUMER_SECRET = 'nPOQXwdUrToovO3QlSLvrOEDjW8n33aFhN69mAxlA', 
		REQUEST_TOKEN_URL = 'https://www.yammer.com/oauth/request_token',
		ACCESS_TOKEN_URL = 'https://www.yammer.com/oauth/access_token', 
		AUTH_URL = 'https://www.yammer.com/oauth/authorize', authKey = '', authSecret = ''):
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
		#resp, content = client.request(url)
		return client

	def database_connect(self):
		cnxn = pyodbc.connect(server)
		cursor = cnxn.cursor()
		return (cnxn, cursor)

	def write_to_stage(self,cursor,cnxn,thread,ID,msg,send,created,source,web):
		cursor.execute('insert into Stage_FACT(Thread_ID,ID,msg,sender_id,created_at,data_source) values (?,?,?,?,?,?)',thread,ID,msg,send,created,source)
		cursor.execute('insert into Stage_dim_msgs(Thread_ID,web_url) values(?,?)',thread,web)
		cnxn.commit()
		print "Message ",ID," added."

	def get_yammer_data(self,cursor,cnxn,client,source='Yammer'):
		i = 0
		go = True
		while i < 10 and go == True:
			try:
				maxa = cursor.execute("select coalesce(max(ID),0) from Stage_FACT").fetchone()[0]
				print "Max id: ", maxa
				url = 'https://www.yammer.com/api/v1/messages/my_feed.xml?newer_than='+str(maxa)
			except:
				url = 'https://www.yammer.com/api/v1/messages/my_feed.xml'
				maxa = 0

			resp,content = client.request(url, 'GET')

			with open('yammer.xml','w') as f:
				f.write(content)
				f.close()
				tree = ET.parse('yammer.xml')
				for elem in tree.iter(tag='messages'):
					for n in elem:
						for nm in n:
							# group = 'None'
							if nm.tag == 'id':
								if nm.text == maxa:
									sys.exit()
								else:
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
					try:
						self.write_to_stage(cursor,cnxn,thread,ID,msg,send,created,source,web)
					except:
						go = False
			i += 1	
			time.sleep(3)