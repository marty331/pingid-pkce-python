import os
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

#redirect_uri = 'https://openidconnect.net/callback' #generic ping test endpoint commonly activated on request. However, you cannot listen here and as such a webform will be needed for manually pasting the ping token.
#redirect_uri = 'http://127.0.0.1:8000/callback' #used for local testing so that you may listen and programatically obtain the token as would happen in production. Spun up by ping team per request.
redirect_uri = 'https://norcoaa-alky-app-dev-webapp.azurewebsites.net/callback'
token_url = "https://sso-dev.shell.com/as/token.oauth2" #static for all of shell
scope = 'openid profile email'#from ping team, may change for each app
authorization_server = 'https://sso-dev.shell.com/as/authorization.oauth2' #static for all of shell
clientID = os.getenv('clientID')
usesql=False #sets up email validation field on top of ping
sqldbPassword = os.getenv('sqldbPassword')
dbServer=os.getenv('dbServer')
dbName=os.getenv('dbName')
sqldbUsername=os.getenv('sqldbUsername')
static_endpoint_testmode=False #should be set to true to use the evergreen 'https://openidconnect.net/callback' test endpoint
