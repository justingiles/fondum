import os

class BaseConfig(object):
    DEBUG = True
    TESTING = True

    SECRET_KEY = 'put secret key here'
    HOST = '0.0.0.0'
    PORT = 8000
    AUTH_EMAILS = "EMAIL1 EMAIL2"  # by default, used by 'determine_admin_flag' in 'custom/login_handler.py' as a space-seperated list
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
    # return urls:
    #   http://{{DOMAIN}}/account/google-oauth2-callback
    #   http://127.0.0.1/player/google-oauth2-callback
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

    def pull_from_environment(self):
        print("CONFIG: examining environment.")
        class_attribs = [v for v in dir(self) if not callable(getattr(self, v)) and not v.startswith("__")]
        # print(class_attribs)
        for key in class_attribs:
            if key in os.environ:
                setattr(self, key, os.environ[key])
                print("CONFIG: {} pulled from environment = {}".format(key, os.environ[key]))
            else:
                print("CONFIG: {} pulled locally.".format(key))


