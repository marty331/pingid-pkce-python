from django.shortcuts import render
from django.http import HttpResponse
import base64 
import os 
import json 
from django.conf import settings
from django.shortcuts import redirect
from pingid.views import _b64_decode, jwt_payload_decode, validate_token
from django.http import HttpResponse

""" landing page control flow, index '/' """
def index(request):
    token = os.getenv("token")
    if token is None:
        return redirect('pingid:login')
    else:
        try:
            jwt_payload_decode(token)
            return redirect('mysite:hello')
        except Exception as e:
            print(f'Token validation issue:\n {e}')
            return redirect('pingid:login')
    return HttpResponse("Welcome to the pingid example app!")

""" /hello app endpoint """
#fake app content, final destination in example, mapped to '/hello'
def hello(request):
    #future post requests in app should not work without a header in the following format -{'token':'Bearer 123faketokenstuff6789'}
    return HttpResponse("Welcome to the fake app landing page, you are authenticated.")

""" /callback app endpoint """
#listener for getting from ping federate after first post request is made. 
def callback(request):
    error_message = None
    code = None
    if 'error' in request.args:
        error_message = request.args['error'] + ':\n' + request.args['error_description']
        response = HttpResponse(error_message)
        response.status_code = 500 
        return response
    else:
        code = request.args['code']
        os.environ['verification_code']=code
        print(f'verification code obtained - {code}')
        return redirect('pingid:obtaintoken')