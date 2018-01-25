from flask_mongoengine import MongoEngine
import datetime
import flask
import logging

db = MongoEngine()

####################################
#
#   USERS (authentication only)
#
####################################


class User(db.Document):
    s_email = db.StringField()         # this is currently a reference email used for admin flag
    s_password = db.StringField(max_length=200)
    #
    s_oauth_email = db.StringField()
    s_oauth_source = db.StringField()  # defaults to "google" for Google OAuth2
    s_oauth_id = db.StringField()

    @property
    def is_active(self):
        return True

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)      # python 3

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def authenticated_email(self):
        return str(self.s_email)

    meta = {'strict': False}


####################################
#
#   ARTICLES
#
####################################


class ArticlePicture(db.Document):
    # the following assumes the use of Amazon S3
    s_url = db.StringField()
    s_etag = db.StringField()
    s_key = db.StringField()
    s_notes = db.StringField()
    dt_uploaded = db.DateTimeField(required=True, default=datetime.datetime.now)

    meta = {'strict': False}


class Article(db.Document):
    s_key = db.StringField(required=True)  # form of group_name/page_name
    s_title = db.StringField()
    s_creole_text = db.StringField()
    dt_last_update = db.DateTimeField(required=True, default=datetime.datetime.now)

    # BLOG Support:
    tf_blog = db.BooleanField(default=False)
    s_blogger_name = db.StringField()
    dt_blog_date = db.DateTimeField()
    s_byline = db.StringField()
    s_img_key = db.StringField()
    arr_blog_categories = db.ListField(db.StringField())


    meta = {'strict': False}

    @property
    def group_name(self):
        keys = self.s_key.split('/')
        if len(keys) == 2:
            return keys[0]
        return ""

    @property
    def page_name(self):
        keys = self.s_key.split('/')
        if len(keys) == 2:
            return keys[1]
        return ""

    @property
    def url(self):
        return "/{}/".format(self.s_key)


class ArticleList(db.Document):
    s_list_type = db.StringField(required=True, default="all")
    arr_articles = db.ListField(db.ReferenceField("Article"))

    meta = {'strict': False}


####################################
#
#    PRODUCTS (or catalog listings in general)
#
####################################


class Product(db.Document):
    s_key = db.StringField(required=True)
    s_title = db.StringField(required=True)
    s_made_by = db.StringField()
    dt_publish_date = db.DateTimeField()
    fl_price = db.DecimalField(force_string=True)
    s_shipping_detail = db.StringField()
    s_short_description = db.StringField()
    s_img_key = db.StringField()
    s_url = db.StringField()
    arr_categories = db.ListField(db.StringField())

    meta = {'strict': False}


#####################################
#
#    LOGGING
#
#####################################

# the following MUST be a duplicate of the constants found in msg.py

FLASK_CAT_LIST = ["message", "success", "info", "warning", "danger"]    

LOG_DESCRIPTION = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.WARNING: "WARNING",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRITICAL"
}

def map_log_to_cat(log_level):
    if log_level < logging.WARNING:
        return "message"
    if log_level < logging.ERROR:
        return "warning"
    return "danger"

DISP_NONE = 0             # don't display at all
DISP_SHOW = 1             # show to end-user; this is the default level; progress continues
DISP_ALERT = 2          # show to end-user; same as "display" but slightly more aggressive

DISP_DESCRIPTION = {
    DISP_NONE: "NONE",
    DISP_SHOW: "SHOW",
    DISP_ALERT: "WARNING",
}

class Logs(db.Document):
    dt_created = db.DateTimeField(required=True, default=datetime.datetime.now)
    s_domain = db.StringField()
    s_instance = db.StringField(default="default")
    s_message = db.StringField()
    s_src = db.StringField()
    s_event_type = db.StringField()
    n_display_level = db.IntField()
    s_display_level = db.StringField()
    n_log_level = db.IntField()
    s_log_level = db.StringField()
    s_return_def = db.StringField()
    s_return_def_parms = db.StringField()
    s_logger_string = db.StringField()
 
    def pull_from_FlashEvent(self, fe):
        self.s_domain = flask.current_app.config.get("DOMAIN", "fondum")
        self.s_message = fe.message
        self.s_event_type = FLASK_CAT_LIST[fe.event_type]
        self.n_display_level = fe.display_level
        self.s_display_level = DISP_DESCRIPTION[fe.display_level]
        self.n_log_level = fe.log_level
        self.s_log_level = LOG_DESCRIPTION[fe.log_level]
        self.s_return_def = fe.return_def
        self.s_return_def_parms = str(fe.return_def_parms)
        self.s_src = "flash"

    def pull_from_logger(self, record):
        self.s_domain = flask.current_app.config.get("DOMAIN", "fondum")
        self.s_message = record.message
        self.s_logger_string = record.formatted_message
        self.s_event_type = map_log_to_cat(record.levelno)
        self.n_log_level = record.levelno
        self.s_log_level = LOG_DESCRIPTION[self.n_log_level]
        self.n_display_level = DISP_NONE  # records directly pulled from logger are never shown to user
        self.s_display_level = DISP_DESCRIPTION[DISP_NONE]
        self.s_return_def_parms = "{}"
        self.s_src = "logger"


# eof
