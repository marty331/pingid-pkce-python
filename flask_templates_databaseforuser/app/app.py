import requests
import base64
import random
import hashlib
import os 
import re
import html 
import webbrowser
from flask_cors import CORS
from flask import redirect, render_template, abort, Flask, request, flash
import jsonify 
from config import Config
from forms import LoginForm
from env import *
import json
from database import connection_url, get_user_list
from waiting import wait
from functools import wraps
from flask_restful import reqparse

app = Flask(__name__)

#get secrets class
app.config.from_object(Config)

#database mode for email auth
if usesql:
    os.environ['valid_emails'] =str(get_user_list(connection_url))

#create way to generate random alphanumeric string of at least length 40 alphanumeric characters, known as the 'verifier'
def generate_code_verifier():
    code_verifier = base64.urlsafe_b64encode(os.urandom(46)).decode('utf-8')
    code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)
    return code_verifier

#create hash of the verifier, then alter it to remove padding of '=' caused by the need to pad bits for base64 encoding
def generate_code_challenge(code_verifier):
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')
    return code_challenge

#validate tokens - https://www.stefaanlippens.net/oauth-code-flow-pkce.html
def _b64_decode(data):
    data += '=' * (4 - len(data) % 4)
    return base64.b64decode(data).decode('utf-8')

def jwt_payload_decode(jwt):
    _, payload, _ = jwt.split('.')
    return json.loads(_b64_decode(payload))

def validate_token(resp, field_to_verify):
    field = json.loads(resp.text).get(field_to_verify)
    try:
        jwt_payload_decode(field)
        return True
    except Exception as e:
        print(f"{field_to_verify} could not be validated\n Cause - {e}")
        return False

@app.route('/')
@app.route('/index')
def index():
    token = os.getenv("token")
    if token is None:
        return redirect('/login')
    else:
        try:
            jwt_payload_decode(token)
            return redirect('/hello')
        except Exception as e:
            print(f'Token validation issue:\n {e}')
            return redirect('/login')
    return "Welcome to the pingid example app!"

#wrapper to validate token in future in app post requests
def token_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        token = request.headers.get('token').split(' ')[1]
        if token!=os.getenv('token'):
            abort(403, description='Bearer token not found in request.')
        return f(*args, **kwargs)

    return wrap

@app.route('/hello')
def fakeapplanding():
    #future post requests in app should not work without a header in the following format -{'token':'Bearer 123faketokenstuff6789'}
    #this may be done with the above token_required wrapper.
    return "Welcome to the fake app landing page, you are authenticated."

#listen for ping redirect. Should be changed to your officially onboarded endpoint which was submitted to the ping team. 
@app.route("/callback")
def callback():
    error_message = None
    code = None
    if 'error' in request.args:
        error_message = request.args['error'] + ':\n' + request.args['error_description']
        abort(500, description=error_message)
    else:
        code = request.args['code']
        os.environ['verification_code']=code
        print(f'verification code obtained - {code}')
        return redirect('/obtaintoken')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if usesql:
        form = LoginForm()
        if form.validate_on_submit():
            flash('Login requested for user {}, remember_me={}'.format(
                form.username.data, form.remember_me.data))
            valid_emails = re.sub('[^@.,A-Za-z0-9]+', '', os.getenv('valid_emails')).split(",")
            if form.username.data not in valid_emails:
                abort(403, description="Username email not found in database. Please refresh the page.")
                return redirect('/login')
            elif os.getenv("token") is None:
                return redirect('/pingauthrequired')
            
        return render_template('login.html', title='Sign In', form=form)
    else:
        return redirect('/pingauthrequired')

#begin ping auth process if user isnt authenticated
@app.route('/pingauthrequired')
def bootup():
    code_verifier = generate_code_verifier()
    os.environ['code_verifier']=code_verifier
    code_challenge = generate_code_challenge(code_verifier)
    #make post request to authorization url bearing the code challenge in order to receive a code used in the next post which obtains the token
    PingTestEndpoint = f'{authorization_server}?client_id={clientID}&response_type=code&code_challenge_method=S256&redirect_uri={redirect_uri}&code_challenge={code_challenge}&scope={scope}'
    webbrowser.open(PingTestEndpoint)
    if os.getenv('static_endpoint_testmode'):
        return render_template('ping-form.html')
    else:
        return 'Please continue using the app via the pingid login tab.'

#use 'code' to authenticate, get bearer token for use with all future post requests within app 
def second_request(clientID, code_verifier, verification_code, redirect_uri, token_url):
    code_verifier = os.getenv("code_verifier")
    payload = { "grant_type":"authorization_code",
                "client_id":clientID,
                "code_verifier":code_verifier,
                "code":verification_code,
                "redirect_uri":redirect_uri
    }
    headers = { 'content-type': "application/x-www-form-urlencoded" }
    response = requests.post(token_url, data=payload, headers=headers)
    return response

#function to wait for the user to login to the ping page, and then for ping federate to post the token to /callback.
def code_checker(code):
    code = os.getenv(code)
    if code is not None:
        return True
    return False
    
#take pasted ping password, redirect to real main app. store token and include in all headers for future posts. 
@app.route('/obtaintoken',  methods=['GET'])
def ping_password_post():
    if os.getenv('static_endpoint_testmode'):
        verification_code = request.form.get('pingidpasscode')
    else:
        #wait for user to login to ping url 
        wait(lambda: code_checker('verification_code'), timeout_seconds=120, waiting_for="Token to be received from listener at /callback")
        verification_code = os.getenv('verification_code')
    code_verifier = os.getenv("code_verifier")
    resp = second_request(clientID, code_verifier, verification_code, redirect_uri, token_url)
    if resp.status_code==200:
        validity = validate_token(resp, 'access_token')
        if validity==False:
            return redirect('/pingauthrequired')
        else:
            os.environ['token'] = json.loads(resp.text).get("access_token")
            return redirect('/hello')

    else:
        return redirect('/pingauthrequired')

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=8000)