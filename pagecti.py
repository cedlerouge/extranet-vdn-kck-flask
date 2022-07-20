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

kck_url = os.getenv("KCK_URL", "https://connect.noumea.nc")
kck_client_id = os.getenv("KCK_CLIENT", "www-noumea.nc")
kck_client_secret = os.getenv("KCK_CLIENT_SECRET", "totototototo")
kck_realm = os.getenv("KCK_REALM", "https://connect.noumea.nc")

port = os.getenv("KCK_FPORT", 8080)


app = Flask(__name__, static_url_path="/templates/")
app.config.update({
    # python -c 'import os; print(os.urandom(16))'
    'SECRET_KEY': b'.\xfb*\xafE\xf5\xa7\x87\xe8\x9b\xff\x80\xb0\xe4\x07\xb9',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPEN_REALM': kck_realm,
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})

oidc = OpenIDConnect(app)

class User():
    username = ""
    email = ""
    user_id = ""
    greeting = ""

    def __init__(self, info_oidc):
        self.username = info_oidc.get('preferred_username')
        self.email = info_oidc.get('email')
        self.user_id = info_oidc.get('sub')
        self.greeting = "Hello %s" % self.username


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

    info = oidc.user_getinfo(['preferred_username', 'email', 'sub'])

    user = User(info)

    return render_template(
        'user.html.j2',
        user=user
    )


if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    logging.info("Starting on port %d", port)
    app.run(port=port)