from django.shortcuts import render
from django.http import HttpResponse
import os 
import re
import base64 
import hashlib
import json
from django.conf import settings
from django.shortcuts import redirect
from .database import connection_url, get_user_list
from django import forms 
from .config import *
import webbrowser

class LoginForm(forms.Form):
    email = forms.EmailField()

#database mode for email auth
if usesql:
    os.environ['valid_emails'] =str(get_user_list(connection_url))

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

""" /login endpoint and control flow """
def login(request):
    if usesql:
        return redirect('pingid:usesql')
    elif os.getenv("token") is None:
        return redirect('pingid:pingauthrequired')
    else:
        return redirect('mysite:hello')

""" /usesql endpoint for checking user submitted email against db"""
def usesql(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            valid_emails = re.sub('[^@.,A-Za-z0-9]+', '', os.getenv('valid_emails')).split(",")
            if form.cleaned_data['email'] not in valid_emails:
                response = HttpResponse("Username email not found in database. Please refresh the page or press back to try again.")
                response.status_code = 403
                return response
            else:
                return redirect('pingid:pingauthrequired')

    return render(request, 'pingid/login.html', {'form': form})


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

""" /pingauthrequired endpoint and control flow """
def pingauthrequired(request):
    code_verifier = generate_code_verifier()
    os.environ['code_verifier']=code_verifier
    code_challenge = generate_code_challenge(code_verifier)
    #make post request to authorization url bearing the code challenge in order to receive a code used in the next post which obtains the token
    PingTestEndpoint = f'{authorization_server}?client_id={clientID}&response_type=code&code_challenge_method=S256&redirect_uri={redirect_uri}&code_challenge={code_challenge}&scope={scope}'
    webbrowser.open(PingTestEndpoint)
    return HttpResponse("Please continue using the app via the pingid login tab.")

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

""" /obtaintoken endpoint and control flow """   
#take pasted ping password, redirect to real main app. store token and include in all headers for future posts. 
def obtaintoken(request):
    wait(lambda: code_checker('verification_code'), timeout_seconds=120, waiting_for="Token to be received from listener at /callback")
    verification_code = os.getenv('verification_code')
    code_verifier = os.getenv("code_verifier")
    resp = second_request(clientID, code_verifier, verification_code, redirect_uri, token_url)
    if resp.status_code==200:
        validity = validate_token(resp, 'access_token')
        if validity==False:
            return redirect('pingid:pingauthrequired')
        else:
            os.environ['token'] = json.loads(resp.text).get("access_token")
            return redirect('mysite:hello')

    else:
        return redirect('pingid:pingauthrequired')