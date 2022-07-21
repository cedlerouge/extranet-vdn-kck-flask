import os

class Config(object):
    pass

class ProdConfig(Config):
    pass

class DevConfig(Config):
    Debug = True
    TESTING = True
    # python -c 'import os; print(os.urandom(16))'
    SECRET_KEY = os.environ.get("SECRET_KEY", b'.\xfb*\xafE\xf5\xa7\x87\xe8\x9b\xff\x80\xb0\xe4\x07\xb9')
    OIDC_CLIENT_SECRETS = 'client_secrets.json'
    OIDC_ID_TOKEN_COOKIE_SECURE = False
    OIDC_REQUIRE_VERIFIED_EMAIL = False
    OIDC_USER_INFO_ENABLED = True
    OIDC_OPEN_REALM = 'integration'
    OIDC_SCOPES = ['openid', 'email', 'profile']
    OIDC_INTROSPECTION_AUTH_METHOD = 'client_secret_post'