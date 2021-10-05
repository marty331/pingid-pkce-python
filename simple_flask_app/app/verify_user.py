from functools import wraps
from flask import request, g, abort
from jwt import decode, exceptions
import base64
import requests
import json


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        authorization = request.headers.get("authorizations", None)
        if not authorization:
            return json.dumps({'error': 'no authorization token provided'}), 403, {'Content-type': 'application/json'}

        try:
            token = authorization.split(' ')[1]
            CLIENT_ID = ''
            ISSUER = ''

            url = ISSUER +"/as/token.oauth2"
            data = {"token": token,"grant_type": "urn:pingidentity.com:oauth2:grant_type:validate_bearer", "client_id": CLIENT_ID}
            headers = {'Content-Type': "application/x-www-form-urlencoded"}
            response = requests.post(url, data=data, headers=headers)
            response_Json = response.json()
            if 'error' not in response_Json:
                print(response_Json)
                g.user = response_Json['access_token']['mail']
            else:
                return json.dumps({'error': 'invalid authorization token/expired token'}), 403, {'Content-type': 'application/json'}

        except exceptions.DecodeError:
            return json.dumps({'error': 'invalid authorization token'}), 403, {'Content-type': 'application/json'}

        return f(*args, **kwargs)

    return wrap



# def role_access(allowed_roles):
#     def decorator(f):
#         @wraps(f)
#         def wrapper():
#             sqlmanager = SQLManager.get_instance()
#             try:
#                 user = g.user
#                 role_id = sqlmanager.get_data(Users, email = user).value(Users.role_id)
#                 role = sqlmanager.get_data(
#                     Roles, role_id=role_id).value(Roles.role)
#                 if role not in allowed_roles:
#                     return json.dumps({'error': 'not authorized to access'}), 401, {'Content-type': 'application/json'}
#             except Exception as ex:
#                 logger.error("Exception occured at role access: {}".format(ex))
#                 return json.dumps({"error": "Error occured at role access level"})

#             return f()
#         return wrapper
#     return decorator
