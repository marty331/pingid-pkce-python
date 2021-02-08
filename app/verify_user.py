from functools import wraps
from flask import request, g, abort
from jwt import decode, exceptions
import base64
import json


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        authorization = request.headers.get("authorizations", None)
        if not authorization:
            return json.dumps({'error': 'no authorization token provided'}), 403, {'Content-type': 'application/json'}

        try:
            token = authorization.split(' ')[1]
            resp = decode(token, None, verify=False, algorithms=['HS256'])
            g.user = resp['mail']
            # code here to validate if user should be part of DAP group 
        except exceptions.DecodeError:
            return json.dumps({'error': 'invalid authorization token'}), 403, {'Content-type': 'application/json'}

        return f(*args, **kwargs)

    return wrap
