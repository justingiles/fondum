class Config(object):
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'put secret key here'
    HOST = '0.0.0.0'
    PORT = 8000
    #
    # MongoDB details
    #
    MONGODB_DB = 'numberposting'
    MONGODB_HOST = 'mongodb://db/numberposting'
    #
    # Amazon S3 details
    #
    S3_LOCATION = 's3.us-east-2.amazonaws.com'
    S3_KEY = 'XXXXXXXXXXXXXXXXXXXX'
    S3_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    S3_UPLOAD_DIRECTORY = 'source_pics'
    S3_BUCKET = 'numberposting-article-pictures'  # this is the default bucket for article pictures
    #
    # Google OAuth2 details
    #
    GOOGLE_OAUTH = {
        'consumer_key': "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com",
        'consumer_secret': "xxxxxxxxxxxxxxxxxxxxxxxx",
        'request_token_params': {
            'scope': 'https://www.googleapis.com/auth/userinfo.email'
        },
        'base_url': 'https://www.googleapis.com/oauth2/v1/',
        'request_token_url': None,
        'access_token_method': 'POST',
        'access_token_url': 'https://accounts.google.com/o/oauth2/token',
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
    }
    # return urls:
    #   http://www.numberposting.life/player/google-oauth2-callback
    #   http://127.0.0.1/player/google-oauth2-callback

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    MONGODB_DB = 'numberposting'
    MONGODB_PASSWORD = 'xxxxxxxxx'
    MONGODB_HOST = "mongodb://numberpostingsite:{}@".format(MONGODB_PASSWORD) + \
        "clusterX-shard-0.domain.com:27017," + \
        "clusterX-shard-1.domain.com:27017," + \
        "clusterX-shard-2.domain.com:27017/" + \
        "{}?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin".format(MONGODB_DB)
    HOST = '0.0.0.0'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True

# eof
