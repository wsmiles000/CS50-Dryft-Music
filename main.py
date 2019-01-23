from __future__ import print_function # In python 2.7
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct, func
from sqlalchemy.orm import scoped_session, sessionmaker
import os
from flask_login import LoginManager
from flask import Blueprint, send_from_directory, request, render_template, redirect, flash, session, url_for, g
from flask_login import login_user, logout_user, current_user, login_required
import json
import pdb
import os
from models import *

#API Import
import sys
import requests
import base64
import urllib
import soundcloud
import jinja2

#define user
global user

#initialize app
app = Flask(__name__)

#link to database
db = SQLAlchemy(app)

#configure database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

#configure Flask loginmanager
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'music'

#API Key
app.secret_key = 'sdfdsaf.23409sdfnlksdfajk43[p[.sadfopk3'

#temporary test db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/music.db'

#API Credentials

# Soundcloud Client Keys 
client = soundcloud.Client(client_id='b8c67b117b4c401d0bf33fa424582e2f',
                           client_secret='75e74dc71f780f742eda6c529235999f',
                           redirect_uri='http://127.0.0.1:5000/callback')

SOUNDCLOUD_CONNECT_URL = "https://soundcloud.com/connect"
SOUNDCLOUD_TOKEN_URL = "https://api.soundcloud.com/oauth2/token"
SOUNDCLOUD_API_BASE_URL = "https://api.soundcloud.com"
SOUNDCLOUD_API_URL = "{}".format(SOUNDCLOUD_API_BASE_URL)

#  Spotify Client Keys
CLIENT_ID = "0a71e6cca357487daa7b0ffaa20e68ad"
CLIENT_SECRET = "c56ffef6094f4246b995fbaf0c587953"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters (Spotify)
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-public"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

#initialize user
@app.before_request
def before_request():
    global user
    user = current_user

#route for homepage
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('music'))
    else:
        return render_template('index.html')

#Flask Login manager
@lm.user_loader
def load_user(id):
    return db.session.query(User).get(int(id))

#Music Homepage
@app.route("/music")
@login_required
def music(): 
    global user
    
    #get spotify access token from the user
    spotify_access_token = user.spotify_access_token
    
    #get soundcloud access token from the user
    soundcloud_access_token = user.soundcloud_access_token
    
    #link to soundcloud API
    import soundcloud
    
    #We will check whether a user is logged into Spotify/Soundcloud or both
    #This will determine which variables to pass and which request to make
    
    if user.spotify_bool == True and user.soundcloud_bool == True:
        
        ######SPOTIFY#######
        
        #Use the access token to access Spotify API
        authorization_header = {"Authorization":"Bearer {}".format(spotify_access_token)}

        # Get profile data
        user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
        profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
        profile_data = json.loads(profile_response.text)

        # Get user playlist data
        playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
        playlist_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        playlist_data = json.loads(playlist_response.text)
        
        # Combine profile and playlist data to display
        display_arr = playlist_data["items"]

        #prepare endpoints for player
        uri_all = []
        for element in display_arr:
            uri_id = element['uri']
            uri_all.append(uri_id)
        
        #######SOUNDCLOUD#######
        
        #create new client with the users access token
        newclient = soundcloud.Client(access_token=soundcloud_access_token)
    
        #get neumber of playlists that the user has
        playlist_count = newclient.get('/me').playlist_count
    
        #prep for player
        url_list = []
    
        #iterate through playlists and prepare them for player
        i = 0
        while i < playlist_count:
            url_list.append(newclient.get('/me/playlists')[i].uri)
            i+=1
        
        url_list = url_list
        
        #show homepage which will display both SC and Spotify playlists
        return render_template('music.html', user=user,uri=uri_all, url_list=url_list)
    
    #here, since the user is only logged into spotify we will only ask for information from spotify
    elif user.spotify_bool == True and user.soundcloud_bool == False:
        ###SPOTIFY
        # Auth Step 6: Use the access token to access Spotify API
        authorization_header = {"Authorization":"Bearer {}".format(spotify_access_token)}

        # Get profile data
        user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
        profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
        profile_data = json.loads(profile_response.text)

        # Get user playlist data
        playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
        playlist_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        playlist_data = json.loads(playlist_response.text)
        
        # Combine profile and playlist data to display
        display_arr = playlist_data["items"]

        #prepare endpoints for player
        uri_all = []
        for element in display_arr:
            uri_id = element['uri']
            uri_all.append(uri_id)
            
        #show music homepage which will display just the Spotify playlists
        return render_template('music.html', user=user,uri=uri_all)
    
    #here, since the user is only logged into SC we will only ask for information from SC
    elif user.spotify_bool == False and user.soundcloud_bool == True:
        
        #create new client with the users access token
        newclient = soundcloud.Client(access_token=soundcloud_access_token)
    
        #get number of playlists that user has
        playlist_count = newclient.get('/me').playlist_count
    
        #prep for player
        url_list = []
    
        #iterate through playlists and prepare them for player 
        i = 0
        while i < playlist_count:
            url_list.append(newclient.get('/me/playlists')[i].uri)
            i+=1
        
        url_list = url_list
        
        #show music homepage which will display just the SC playlists
        return render_template('music.html',user=user,url_list=url_list)
    
    #if user is logged into neither soundcloud then just greet them
    else:
        return render_template('music.html',user=user)
    
    
#shows signup page
@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

#accept data from signup form and signup user
@app.route('/signUp', methods=['Post'])
def signUp():
    global user
    
    #assign form data to variables
    username = request.form['inputName'].capitalize()
    email = request.form['inputEmail'].lower()
    password = request.form['inputPassword']
    
    #check if username is taken
    if db.session.query(User).filter(User.username == username).first() is not None:
        flash('Account already exists for this Username! Please try signing in.')
        return redirect(url_for('user.login'))
    
    #check if email is taken
    if db.session.query(User).filter(User.email == email).first() is not None:
        flash('Account already exists for this email address! Please try signing in.')
        return redirect(url_for('user.login'))
    
    #assign values to user
    user = User(username=username, email=email, spotify_bool=False, soundcloud_bool=False)
    
    #hash password
    user.hash_password(password)
    
    #add user to database
    db.session.add(user)
    db.session.commit()
    
    #log user in
    login_user(user)
    
    #redirect to music hompepage
    return redirect(url_for('music'))
       
#show sign in page
@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')

#get data from formm and sign user in
@app.route('/signIn', methods =['Post'])
def signIn():
    global user
    
    #fill form on redirect
    if request.method == 'GET':
        email = request.args.get('defaultEmail')
        return render_template('login.html', defaultEmail=email)
    
    #assign form data to variables
    email = request.form['inputEmail'].lower()
    password = request.form['inputPassword']
    
    #search database for user
    user = db.session.query(User).filter(User.email == email).first()
    
    #if user doesn't exist let them know
    if user is None:
        flash('Email is invalid!')
        return redirect(url_for('signIn'))
    
    #check if password matches email
    if user.verify_password(password) is False:
        flash('Password is invalid!')
        return redirect(url_for('signIn'))
    
    #login the user
    login_user(user)
    
    #redirect to music homepage
    return redirect(url_for('music'))

#log out the user
@app.route("/logout")
@login_required
def logout():
    
    #delink spotify and soundcloud
    user.spotify_bool = False
    db.session.commit()
    user.soundcloud_bool = False
    
    #logout the user
    logout_user()
    flash("You have logged out")
    
    #redirect to homepage
    return redirect(url_for("index"))

#show the link accounts page
@app.route("/linkaccounts")
@login_required
def link():
    return render_template('link.html')

########## API Routing ##########

#spotify authorization
@app.route("/spotify")
def spotify():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.quote(val)) for key,val in auth_query_parameters.iteritems()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

#show spotify redirect (used for authorization)
@app.route("/soundcloud")
def soundcloud():
    return redirect(client.authorize_url())

#Spotify Callback Route
@app.route("/callback/q")
def callback():
    global user
    
    #Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    
    #add token to database
    user.spotify_access_token = access_token
    db.session.commit()

    #store in database that user has connected to Spotify
    user.spotify_bool = True
    db.session.commit()
    
    #redirect to music
    return redirect(url_for('music', access_token = user.spotify_access_token))

#Soundcloud Callback Route
@app.route("/callback")
def call():
    #links soundcloud api information
    import soundcloud
    
    #code that is stored as a query in the authorization page; Use the get method to retrieve this query and store the code
    code=request.args.get('code')
    
    #client.exchange_token is a function that takes the stored code and returns an access_token for user data
    token = client.exchange_token(code)
    
    #save soundcloud access token to database
    user.soundcloud_access_token = token.access_token
    db.session.commit()
    
    #save to database that user has linked to soundcloud
    user.soundcloud_bool = True
    db.session.commit()
      
    #redirect to music homepage
    return redirect(url_for('music'))

#run app
if __name__ == "__main__":
    app.run(debug=True, port=PORT)