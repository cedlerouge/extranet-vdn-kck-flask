#!/usr/bin/env python

import logging
import os
import json

from flask import (
    Flask,
    g,
    request,
    Response,
    render_template,
    flash,
    redirect,
    url_for,
)
from flask_oidc import OpenIDConnect
import pprint
from config import DevConfig
from keycloak import KeycloakOpenID

kck_url = os.getenv("KCK_URL", "https://connect.noumea.nc")
kck_client_id = os.getenv("KCK_CLIENT", "www-noumea.nc")
kck_client_secret = os.getenv("KCK_CLIENT_SECRET", "totototototo")
kck_realm = os.getenv("KCK_REALM", "https://connect.noumea.nc")


host = os.getenv("FLASK_HOST", "0.0.0.0")
port = os.getenv("FLASK_PORT", 8080)


app = Flask(__name__, static_url_path="/templates/")
app.config.from_object(DevConfig)
#app.config.update({
#    # python -c 'import os; print(os.urandom(16))'
#    'SECRET_KEY': b'.\xfb*\xafE\xf5\xa7\x87\xe8\x9b\xff\x80\xb0\xe4\x07\xb9',
#    'TESTING': True,
#    'DEBUG': True,
#    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
#    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
#    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
#    'OIDC_USER_INFO_ENABLED': True,
#    'OIDC_OPEN_REALM': kck_realm,
#    'OIDC_SCOPES': ['openid', 'email', 'profile'],
#    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
#})

def configKckOIDC(json_file):

    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        pprint.pprint(data)
        
        return KeycloakOpenID(server_url=data['web']['auth_uri'],
            client_id=data['web']['client_id'],
            client_secret_key=data['web']['client_secret'],
            realm_name=data['web']['issuer'].split('/')[-1])
    except Exception as e:
        print("ERROR: ", e)
        raise

        


oidc = OpenIDConnect(app)
json_file = app.config['OIDC_CLIENT_SECRETS']
keycloak_openid = configKckOIDC(json_file)

#server_url=app.config.web.auth_uri,
#    client_id="example_client",
#    realm_name="example_realm",
 #   client_secret_key="secret")

class User():
    username = ""
    email = ""
    email_verified = ""
    user_id = ""
    birthdate = ""
    birthplace = ""
    gender = ""
    given_name = ""
    family_name = ""
    preferred_name = ""
    verified = ""
    greeting_name = ""

    def __init__(self, info_oidc):
        self.username = info_oidc.get('preferred_username')
        self.email = info_oidc.get('email')
        self.email_verified = info_oidc.get('email_verified')
        self.user_id = info_oidc.get('sub')
        self.birthdate = info_oidc.get('birthdate')
        self.birthplace = info_oidc.get('birthplace')
        self.gender = info_oidc.get('gender')
        self.given_name = info_oidc.get('given_name')
        self.family_name = info_oidc.get('family_name')
        self.preferred_name = info_oidc.get('preferred_name')
        self.greeting = "Hello {0} {1}".format(self.given_name, self.preferred_name if self.preferred_name != "" else self.family_name)


@app.route("/")
def home():
    if oidc.user_loggedin:
        return render_template(
            'home.html.j2',
            username=oidc.user_getfield('preferred_username')
        )
    else:
        return render_template(
            'home.html.j2',
            username=""
        )

@app.route('/private')
@oidc.require_login
def hello_me():
    """ Example for protected endproint that extracs private information from the OpenID Connect id_token
        Uses the accompagnied access_token to access a backend service.
    """

    info = oidc.user_getinfo([
        'preferred_username',
        'email',
        'email_verified',
        'preferred_name',
        'family_name',
        'given_name',
        'birthdate',
        'birthplace',
        'gender',
        'sub'])

    user = User(info)

    return render_template(
        'user.html.j2',
        user=user
    )

@app.route('/logout')
@oidc.require_login
def logout():
    """Performs local logout by removing the session cookie."""


    url = oidc.client_secrets.get('issuer')
    # TODO use dynamic uri
    hosturl = 'http%3A%2F%2F172.16.24.111%3A8080%2F'
    pprint.pprint(oidc)
    refresh_token = oidc.get_refresh_token()
    print("logout")
    pprint.pprint(refresh_token)
    oidc.logout()
    return redirect(
        url + '/protocol/openid-connect/logout?redirect_uri=' + hosturl)
    #keycloak_openid.logout(refresh_token)
    #return render_template(
    #   'logout.html.j2'
    #)

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    logging.info("Starting on port %d", port)
    app.run(port=port, host=host)