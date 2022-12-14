import os
import flask
from flask import Flask, render_template, url_for, redirect
from authlib.integrations.flask_client import OAuth

import google_api_stuff.drive as report_app
import google_api_stuff.acc as acc
import google_api_stuff.tasks as tasks_app
#import google_api_stuff.calendar as google_calendar

app = Flask(__name__)
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY", default=False)

oauth = OAuth()
oauth.init_app(app)

app.register_blueprint(report_app.report_app)
app.register_blueprint(tasks_app.goals_app)

app.config['SERVER_NAME'] = 'localhost:8000'

@app.route('/')
def index():
    # If user is already logged in
    if 'google_token' in flask.session:
        return render_template(
            'index.html', 
            name = flask.session['user_name'],
            dob = acc.get_birthday(flask.session['google_token']),
            )
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
            'scope': 'openid email profile https://www.googleapis.com/auth/tasks https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/user.birthday.read'
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
    # get user name from google
    flask.session['user_name'] = user['name']
    return redirect('/')
