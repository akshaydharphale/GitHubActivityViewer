from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
import os
import yaml
import json
import sys
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)


# This information is obtained upon registration of a new GitHub
client_id = "registered_Application_client_Id"
client_secret = "registeredApplication_secret"
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'


@app.route("/")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    github = OAuth2Session(client_id)
    authorization_url, state = github.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback/", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    github = OAuth2Session(client_id, state=session['oauth_state'])
    token = github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token
    return redirect(url_for('.profile'))


@app.route("/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    github = OAuth2Session(client_id, token=session['oauth_token'])
    recJson = json.dumps(github.get('https://api.github.com/user').json())
    recDic = json.loads(recJson)
    eventUrl = recDic['received_events_url']
    eventDic = json.loads(json.dumps(github.get(eventUrl).json()))
    i = 0
    responseJson = "["
    for event in eventDic:
        responseJson = responseJson +  '{"EventRepository":" '+eventDic[i]['repo']['name']+'","EventType":"'+eventDic[i]['type']+'"},'
        i = i + 1

    responseJson = responseJson + '{"EndOfEvent":"FinalEvent"}]'
    #print responseJson
    return jsonify(json.loads(responseJson))


app.secret_key = os.urandom(24)

if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)
    app.debug = True
    app.run()
