import os 
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# load in environment variables/secrets
RELEASE_VERSION ='2.' + open('environment/release.version.env', 'r').read()

# condition on deployment environment (e.g. local/staging/prod)
if 'DEPLOYMENT_ENVIRONMENT' not in os.environ:
    DEPLOYMENT_ENVIRONMENT = 'local'
    
    # app secrets
    BACKEND_TOKEN = open('environment/backend.token.secret', 'r').read()
    DASH_PASSWORD = open('environment/password.secret','r').read()
    DATABASE_PASSWORD = open('environment/database.secret','r').read()

    """ it is possible to use 0auth online for free to emulate a ping federate
        If you do so and make the according secrets below,
        this emulated federate will be active on your local run."""
    # oauth0 secrets
    if os.getenv('localauth0') == "True":
        CLIENT_ID = open('environment/oauth0/client.id.secret').read()
        SECRET_KEY = open('environment/oauth0/secret.key').read()
        USER_INFO_EMAIL = 'email'
        DOMAIN = ''
        DOMAIN_URL = f'https://{DOMAIN}'
        DOMAIN_AUTH_URL = f'https://{DOMAIN}/authorize'
        DOMAIN_TOKEN_URL = f'https://{DOMAIN}/oauth/token'
        DOMAIN_USER_URL = f'https://{DOMAIN}/userinfo'
        DOMAIN_LOGOUT_URL = f'https://{DOMAIN}/v2/logout'
        DOMAIN_SCOPE = 'openid profile email'
        AUTH_REDIRECT_URI = 'http://localhost:8050/callback'

else:
    DEPLOYMENT_ENVIRONMENT = os.getenv('DEPLOYMENT_ENVIRONMENT')

    # azure keyvault secrets 
    keyVaultName = ''
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    BACKEND_TOKEN = client.get_secret('backend-token').value
    DASH_PASSWORD = client.get_secret('dash-password').value
    DATABASE_PASSWORD = client.get_secret('database-password').value
    CLIENT_ID = client.get_secret('ping-client-id').value
    SECRET_KEY = client.get_secret('flask-server-key').value

    # environment specific
    if DEPLOYMENT_ENVIRONMENT == 'staging':
        DOMAIN = 'sso-uat.shell.com'
        AUTH_REDIRECT_URI = 'https://{}-dash-staging.azurewebsites.net/callback'
    elif DEPLOYMENT_ENVIRONMENT == 'prod':
        DOMAIN = 'sso-dev.shell.com'
        AUTH_REDIRECT_URI = 'https://{}-dash.azurewebsites.net/callback'
    
    # oauth0 secrets
    USER_INFO_EMAIL = 'mail'
    DOMAIN_URL = f'https://{DOMAIN}'
    DOMAIN_AUTH_URL = f'https://{DOMAIN}/as/authorization.oauth2'
    DOMAIN_TOKEN_URL = f'https://{DOMAIN}/as/token.oauth2'
    DOMAIN_USER_URL = f'https://{DOMAIN}/idp/userinfo.openid'
    DOMAIN_LOGOUT_URL = f'https://{DOMAIN}/as/revoke_token.oauth2'
    DOMAIN_SCOPE = 'openid profile email'
