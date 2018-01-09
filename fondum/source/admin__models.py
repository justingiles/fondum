from flask_mongoengine import MongoEngine
import datetime

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


# eof
