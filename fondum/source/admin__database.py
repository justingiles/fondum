import admin__models as models
import mongoengine as db
from app import bcrypt
from decimal import Decimal

from PLOD import PLOD

import msg

# TODO: remove PLOD since this is generic

def _parse_cats(data):
    cats = data.split(",")
    return [c.strip() for c in cats]



########################################
#
#    USER LOGIN
#
########################################


def create_user_byOAuth(email, authid, source):
    #
    # check for duplicate email
    #
    found_duplicate = True
    try:
        models.User.objects.get(s_oauth_email=email)
    except db.DoesNotExist:
        found_duplicate = False
    except db.MultipleObjectsReturned:
        return msg.bug("Internal error: multiple users found. Please contact us.")
    if found_duplicate:
        return msg.bug("Please contact us, duplicate emails found.")
    #
    # create
    #
    user = models.User()
    user.s_email = email
    user.s_oauth_email = email
    user.s_oauth_id = authid
    user.s_oauth_source = source
    user.save()
    return user


def read_user(user_id):
    try:
        user = models.User.objects.get(id=user_id)
    except db.DoesNotExist:
        return msg.err("Account {} not found.".format(user_id))
    except db.MultipleObjectsReturned:
        return msg.err("Duplicate IDs found.")
    return user


def read_user_byOAuth(email, authid, source):
    try:
        user = models.User.objects.get(s_oauth_email=email, s_oauth_id=authid, s_oauth_source=source)
    except db.DoesNotExist:
        user = msg.err("Account does not exist.")
    return user


############################################
#
#    ARTICLES
#
############################################


def _save_article(article):
    article.save()
    update_articleList_universal()
    return


def _good_key_check(key):
    s = key.split("/")
    if len(s) != 2:
        return False
    return True


def build_key(group_name, page_name):
    key = "{}/{}".format(group_name, page_name)
    return key


def create_article(key, wtf):
    if not _good_key_check(key):
        return msg.err("{} is not a valid group/page combination.".format(key))
    article = models.Article()
    article.s_key = key
    article.s_title = wtf.s_title.data
    article.s_creole_text = wtf.s_creole_text.data

    article.tf_blog = wtf.blog.tf_blog.data
    article.s_blogger_name = wtf.blog.s_blogger_name.data
    article.dt_blog_date = wtf.blog.dt_blog_date.data
    article.s_byline = wtf.blog.s_byline.data
    article.s_img_key = wtf.blog.s_img_key.data
    article.arr_blog_categories = _parse_cats(wtf.blog.categories.data)
    #
    # all is good. Save everything.
    #
    _save_article(article)
    return article


def read_article_byKey(key):
    try:
        a = models.Article.objects.get(s_key=key)
    except db.DoesNotExist:
        a = None
    return a


def update_article(article, wtf):
    article.s_title = wtf.s_title.data
    article.s_creole_text = wtf.s_creole_text.data

    article.tf_blog = wtf.blog.tf_blog.data
    article.s_blogger_name = wtf.blog.s_blogger_name.data
    article.dt_blog_date = wtf.blog.dt_blog_date.data
    article.s_byline = wtf.blog.s_byline.data
    article.s_img_key = wtf.blog.s_img_key.data
    article.arr_blog_categories = _parse_cats(wtf.blog.categories.data)

    _save_article(article)
    return article


def delete_article(key):
    try:
        a = models.Article.objects.get(s_key=key)
        a.delete()
        update_articleList_universal()
    except db.DoesNotExist:
        return msg.err("could not find {}".format(key))
    return a


def upsert_article(key, wtf):
    article = read_article_byKey(key)
    if msg.is_bad(article):
        return create_article(key, wtf)
    return update_article(article, wtf)


#
# articleList items
#

def read_articleList(list_type="all"):
    # note: only 'all' and 'blog' are really supported.
    try:
        lst = models.ArticleList.objects.get(s_list_type=list_type)
    except db.DoesNotExist:
        lst = None
    if not lst:
        lst = models.ArticleList(s_list_type=list_type)
        lst.arr_articles = []
        lst.save()
    return lst


def read_articleList_asProducts(list_type="blog"):
    unsorted = []
    al = read_articleList(list_type=list_type)
    by_date = PLOD(al.arr_articles).sort('dt_blog_date', reverse=True).returnList()
    for entry in by_date:
        p = models.Product()
        p.s_key = entry.s_key
        p.s_title = entry.s_title
        p.s_made_by = entry.s_blogger_name
        p.dt_publish_date = entry.dt_blog_date
        p.fl_price = "0.00"
        p.s_shipping_detail = str(entry.dt_blog_date)
        p.s_short_description = entry.s_byline
        p.s_img_key = entry.s_img_key
        p.s_url = entry.url
        p.arr_categories = entry.arr_blog_categories
        unsorted.append(p)
    return unsorted


def update_articleList_all():
    lst = read_articleList(list_type="all")
    lst.arr_articles = []
    bulk = models.Article.objects
    for article in bulk:
        lst.arr_articles.append(article)
    lst.save()
    return


def update_articleList_blog():
    lst = read_articleList(list_type="blog")
    lst.arr_articles = []
    bulk = models.Article.objects(tf_blog=True)
    for article in bulk:
        lst.arr_articles.append(article)
    lst.save()
    return

def update_articleList_universal():
    update_articleList_all()
    update_articleList_blog()
    return


###################################################
#
#    PICTURES
#
###################################################


def read_articlePicture(key):
    try:
        p = models.ArticlePicture.objects.get(s_key=key)
    except db.DoesNotExist:
        p = None
    return p



def readlist_articlePictures():
    try:
        apl = models.ArticlePicture.objects
    except db.DoesNotExist:
        apl = []
    return apl



def upsert_articlePicture(key, wtf, details):
    p = read_articlePicture(key)
    if p:  # this is an update not an insert/create
        if details["success"]:  # but a new file was uploaded
            p.s_url = details['url']
            p.s_etag = details['etag']
            p.s_key = key
            p.s_notes = wtf.s_notes.data
            p.save()
            return msg.success("uploaded replacement file.")
        p.s_notes = wtf.s_notes.data
        p.s_key = key
        p.save()
        return msg.success("changed details about file.")
    p = models.ArticlePicture()
    p.s_url = details['url']
    p.s_etag = details['etag']
    p.s_key = key
    p.s_notes = wtf.s_notes.data
    p.save()
    return msg.success('uploaded "{}"'.format(details['name']))


###################################################
#
#    PRODUCT
#
###################################################


def create_product(key, wtf):
    p = models.Product()
    p.s_key = wtf.s_key.data
    p.s_title = wtf.s_title.data or "[NO TITLE]"
    p.s_made_by = wtf.s_made_by.data or None
    try:
        p.fl_price = Decimal(wtf.fl_price.data)
    except:
        p.fl_price = None
    p.s_shipping_detail = wtf.s_shipping_detail.data or None
    p.s_short_description = wtf.s_short_description.data or ""
    p.s_img_key = wtf.s_img_key.data or None
    p.s_url = wtf.s_url.data
    cats = wtf.categories.data.split(",")
    p.arr_categories = [c.strip() for c in cats]
    p.save()
    return msg.success("Product {} added.".format(p.s_key))


def read_product(key):
    try:
        p = models.Product.objects.get(s_key=key)
    except db.DoesNotExist:
        p = msg.bug("Product {} does not exist.".format(key))
    return p


def update_product(product, wtf):
    product.s_title = wtf.s_title.data or "[NO TITLE]"
    product.s_made_by = wtf.s_made_by.data or None
    try:
        product.fl_price = Decimal(wtf.fl_price.data)
    except:
        product.fl_price = None
    product.s_shipping_detail = wtf.s_shipping_detail.data or None
    product.s_short_description = wtf.s_short_description.data or ""
    product.s_img_key = wtf.s_img_key.data or None
    product.s_url = wtf.s_url.data
    cats = wtf.categories.data.split(",")
    product.arr_categories = [c.strip() for c in cats]
    product.save()
    return msg.success("Product {} updated.".format(product.s_key))


def delete_product(key):
    product = read_product(key)
    if msg.is_bad(product):
        return msg.err("Product {} missing; possibly already deleted.".format(key))
    product.delete()
    return msg.success("Product {} deleted.".format(product.s_key))


def upsert_product(key, wtf):
    product = read_product(key)
    if msg.is_good(product):
        return update_product(product, wtf)
    return create_product(key, wtf)


# the following is not efficient; but that should not really matter.
def readlist_product(categories=None):
    pl = models.Product.objects
    final = []
    for p in pl:
        if not categories:
            final.append(p)
        else:
            for category in categories:
                if category in p.arr_categories:
                    final.append(p)
                    break
    return final

# eof
