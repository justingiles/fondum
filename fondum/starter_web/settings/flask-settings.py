from baseconfig import BaseConfig
import logging


class Config(BaseConfig):
    SECRET_KEY = 'put secret key here'
    HOST = '0.0.0.0'
    PORT = 8000
    DOMAIN = "{{DOMAIN}}"
    AUTH_EMAILS = "EMAIL1 EMAIL2"  # by default, used by 'determine_admin_flag' in 'custom/login_handler.py' as a space-seperated list
    #
    # Logging details
    #
    HAS_LOGGING = True
    # details for LOGGING_FORMAT at https://docs.python.org/2/library/logging.html#logrecord-attributes
    LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s,%(lineno)d - %(message)s"
    LOGGING_LEVEL = logging.WARNING
    #
    # MongoDB details
    #
    MONGODB_DB = 'fondum_{{SAFE_DOMAIN}}'
    MONGODB_HOST = 'mongodb://db/fondum_{{SAFE_DOMAIN}}'
    #
    # Amazon S3 details
    #
    S3_LOCATION = 's3.us-east-2.amazonaws.com'
    S3_KEY = 'XXXXXXXXXXXXXXXXXXXX'
    S3_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    S3_UPLOAD_DIRECTORY = 'source_pics'
    S3_BUCKET = 'fondum-{{SAFE_DOMAIN}}-article-pictures'  # this is the default bucket for article pictures
    #
    # Google OAuth2 details
    #
    # return urls to authorize in the Google Developer Console:
    #
    #   http://{{DOMAIN}}.localtest.me/account/google-oauth2-callback/new
    #   http://{{DOMAIN}}/account/google-oauth2-callback/new
    #   http://{{DOMAIN}}.localtest.me/account/google-oauth2-callback/current
    #   http://{{DOMAIN}}/account/google-oauth2-callback/current
    #
    GOOGLE_OAUTH = {
        'consumer_key': "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com",
        'consumer_secret': "xxxxxxxxxxxxxxxxxxxxxxxx",
        'request_token_params': {
            'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'
        },
        'base_url': 'https://www.googleapis.com/oauth2/v1/',
        'request_token_url': None,
        'access_token_method': 'POST',
        'access_token_url': 'https://accounts.google.com/o/oauth2/token',
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
    }
    #
    # SendGrid details
    #
    HAS_SENDMAIL = False
    SENDGRID_UNSUBSCRIBE_GROUPS = {
        1: "Announcements",
    }
    SENDGRID_DEFAULT_FROM_ADDRESS = None
    SENDGRID_DEFAULT_SUBJECT = None
    SENDGRID_API_KEY = "to-be-determined"
    #
    # Flattr Support
    #
    HAS_TIPPING = False
    FLATTR_ID = "to-be-determined"



class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # MONGODB_DB = 'numberposting'
    # MONGODB_PASSWORD = 'xxxxxxxxx'
    # MONGODB_HOST = "mongodb://numberpostingsite:{}@".format(MONGODB_PASSWORD) + \
    #     "clusterX-shard-0.domain.com:27017," + \
    #     "clusterX-shard-1.domain.com:27017," + \
    #     "clusterX-shard-2.domain.com:27017/" + \
    #     "{}?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin".format(MONGODB_DB)
    # HOST = '0.0.0.0'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True

# eof
