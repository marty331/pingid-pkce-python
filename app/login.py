import base64
import hashlib
import json
import os
import pathlib
import requests
import secrets
import threading
import urllib
import webbrowser
from time import sleep

from werkzeug.serving import make_server

import dotenv
from flask import Flask, request

app = Flask(__name__)

class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server('localhost', 3000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print('starting server')
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


def url_encode(byte_data):
    return base64.urlsafe_b64encode(byte_data).decode('utf-8').replace('=', '')


def generate_challenge(a_verifier):
    return url_encode(hashlib.sha256(a_verifier.encode()).digest())


env_path = pathlib.Path('.') / '.env'
dotenv.load_dotenv(dotenv_path=env_path)

verifier = url_encode(secrets.token_bytes(32))
challenge = generate_challenge(verifier)
state = url_encode(secrets.token_bytes(32))
client_id = os.getenv('CLIENT_ID')
redirect_uri = os.getenv('REDIRECT_URI')
pingenv = os.getenv('PING_ENV')  # -dev, -uat

# We generate a nonce (state) that is used to protect against attackers invoking the callback
base_url = 'https://sso%s.shell.com/as/authorization.oauth2' % pingenv +'?'
url_parameters = {
    'audience': redirect_uri,
    # 'scope': 'profile email firstname lastname',
    'response_type': 'code',
    'redirect_uri': redirect_uri,
    'client_id': client_id,
    'code_challenge': challenge.replace('=', ''),
    'code_challenge_method': 'S256',
    # 'state': state
}
url = base_url + urllib.parse.urlencode(url_parameters)

received_callback = False
webbrowser.open_new(url)
server = ServerThread(app)
server.start()
while not received_callback:
    sleep(1)
server.shutdown()

if state != received_state:
    print("Error: session replay. Please log out of all connections.")
    exit(-1)

if error_message:
    print("An error occurred:")
    print(error_message)
    exit(-1)

# Exchange the code for a token
url = 'https://sso%s.shell.com/as/token.oauth2' % pingenv
headers = {'Content-Type': 'application/json'}
body = {'grant_type': 'authorization_code',
        'client_id': client_id,
        'code_verifier': verifier,
        'code': code,
        'audience': redirect_uri,
        'redirect_uri': redirect_uri}
r = requests.post(url, headers=headers, data=json.dumps(body))
data = r.json()

# Use the token to list the clients
url = 'https://sso%s.shell.com/as/authorization.oauth2' % pingenv
headers = {'Authorization': 'Bearer %s' % data['access_token']}
r = requests.get(url, headers=headers)
data = r.json()

for client in data:
    print("Client: " + client['name'])


@app.route("/callback")
def callback():
    global received_callback, code, error_message, received_state
    error_message = None
    code = None
    if 'error' in request.args:
        error_message = request.args['error'] + \
            ': ' + request.args['error_description']
    else:
        code = request.args['code']
    received_state = request.args['state']
    received_callback = True
    return "return to application now."
