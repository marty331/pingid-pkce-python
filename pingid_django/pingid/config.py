import os 
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
env ='local'

token_url = "https://sso-dev.shell.com/as/token.oauth2" #static for all of shell
scope = 'openid profile email'#from ping team, may change for each app
authorization_server = 'https://sso-dev.shell.com/as/authorization.oauth2' #static for all of shell
usesql=True #sets up email validation field on top of ping
redirect_uri='http://127.0.0.1:8000/callback' #localhost urls for ping must be spun up by a pingid team member


if os.environ.get('env') == 'local' or env=='local':
    clientID = os.getenv('devclientID')
    sqldbPassword = os.getenv('sqldbPassword')
    dbServer = os.getenv('dbServer')
    dbName = os.getenv('dbName')
    sqldbUsername = os.getenv('sqldbUsername')

else:
    # azure keyvault secrets 
    keyVaultName = os.getenv('KVNAME')
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)

    clientID = client.get_secret('prodclientID').value
    sqldbPassword = client.get_secret('sqldbPassword').value
    dbServer = client.get_secret('dbServer').value
    dbName = client.get_secret('dbName').value
    sqldbUsername = client.get_secret('sqldbUsername').value

