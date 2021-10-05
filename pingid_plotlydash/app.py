# dash modules
import dash
import dash_auth
import os
from dash import html
from env import DASH_PASSWORD, DEPLOYMENT_ENVIRONMENT
from dash_custom_oauth.custom_oauth import CustomOAuth

# dash application
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server


# condition on deployment environment (e.g. local/staging/prod)
if 'DEPLOYMENT_ENVIRONMENT' not in os.environ:
    debug=True
    #toggle to swap oauth0 and dash's out of box basichttpauth
    os.environ['localauth0'] = 'False'
    #set up basic http un and pw 
    VALID_USERNAME_PASSWORD_PAIRS = {}
    VALID_USERNAME_PASSWORD_PAIRS["user"] = DASH_PASSWORD
    if os.getenv('localauth0') == "True":
        auth = CustomOAuth(app)
    else:
        auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

else:
    debug=False
    if DEPLOYMENT_ENVIRONMENT == 'staging':
        auth = CustomOAuth(app)
    elif DEPLOYMENT_ENVIRONMENT == 'prod':
        auth = CustomOAuth(app)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    ''')
])

if __name__ == '__main__':    
    if debug:
        app.run_server(
            host="0.0.0.0",
            port=8050,
            debug=debug
        )
    else:
        app.run_server(
            debug=debug
        )