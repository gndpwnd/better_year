import os
import flask
from flask import Flask, render_template, url_for, redirect

from authlib.integrations.flask_client import OAuth

#import google_api_stuff.drive as google_drive
#import google_api_stuff.tasks as google_tasks
#import google_api_stuff.calendar as google_calendar


app = Flask(__name__)
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY", default=False)

oauth = OAuth()
oauth.init_app(app)

#app.register_blueprint(google_drive.app)

'''
	Set SERVER_NAME to localhost as twitter callback
	url does not accept 127.0.0.1
	Tip : set callback origin(site) for facebook and twitter
	as http://domain.com (or use your domain name) as this provider
	don't accept 127.0.0.1 / localhost
'''

@app.route('/')
def index():
    # If user is already logged in
    if 'google_token' in flask.session:
        return render_template('index.html')
    else:
        return render_template('need_auth.html')

@app.route('/google/')
def google():
   
    # Google Oauth Config
    # Get client_id and client_secret from environment variables
    # For developement purpose you can directly put it
    # here inside double quotes
    GOOGLE_CLIENT_ID = os.environ.get('FN_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('FN_CLIENT_SECRET')
     
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
     
    # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
 
@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token, nonce=None)
    print(" Google User ", user)
    # add the token to the session
    flask.session['google_token'] = token
    return redirect('/')

@app.route('/report')
def report():
    return 'This is the report page'

@app.route('/macro_goals')
def macro_goals():
    return 'This is the macro goals page'

@app.route('/micro_goals')
def micro_goals():
    return 'This is the micro goals page'
