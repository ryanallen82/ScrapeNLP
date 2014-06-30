import urllib2
from ntlm import HTTPNtlmAuthHandler
from sharepoint import SharePointSite
import getpass

site_url = "https://collab.mayo.edu/team/EASI/SI/SitePages/Home.aspx"
user = 'mfad\m097654'
pwd = getpass.getpass('Password:')

passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None,site_url,user,pwd)
auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
opener = urllib2.build_opener(auth_NTLM)
#urllib2.install_opener(opener)

site = SharePointSite(site_url,opener)

print site.lists
for sp_list in site.lists:
	print sp_list