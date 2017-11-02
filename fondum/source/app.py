from flask import Flask, request, g, redirect, url_for, \
    render_template, flash, Markup, send_file
from flask_bcrypt import Bcrypt
from flask_mongoengine import MongoEngine
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_qrcode import QRcode
from flask_oauthlib.client import OAuth
import os
import sys
import babel

CLAIM_COST = 10
DAILY_ALLOWANCE = 20

# thanks to
#   http://stackoverflow.com/questions/12339806/escape-strings-for-javascript-using-jinja2
_js_escapes = {
    '\\': '\\u005C',
    '\'': '\\u0027',
    '"': '\\u0022',
    '>': '\\u003E',
    '<': '\\u003C',
    '&': '\\u0026',
    '=': '\\u003D',
    '-': '\\u002D',
    ';': '\\u003B',
    u'\u2028': '\\u2028',
    u'\u2029': '\\u2029'
}
# the following is for python 2/3 compatibility
try:
    xrange
except NameError:
    xrange = range
# Escape every ASCII character with a value less than 32.
_js_escapes.update(('%c' % z, '\\u%04X' % z) for z in xrange(32))


def jinja2_escapejs_filter(value):
    retval = []
    for letter in value:
        if letter in _js_escapes:
            retval.append(_js_escapes[letter])
        else:
            retval.append(letter)
    return Markup("".join(retval))


CATEGORY_HTML = {
    "message": "&#x2709;",  # envelope
    "success": "&#x2713;",  # checkmark
    "info": "&#x2139;",     # 'i' symbol
    "warning": "&#x26a0;",  # exclamation triangle
    "danger": "&#x274c;",   # cross mark
}


def jinja2_category_icon_filter(value):
    if value in CATEGORY_HTML:
        return CATEGORY_HTML[value]
    return ">"


def jinja2_creole_top(value):
    return parsing.first_paragraph_html(value)


def jinja2_USD(value, fmt=None, prec=2, dollar_sign=True):
    if not fmt:
        fmt = "${:,.2f}"
    if prec != 2:
        fmt = "${:,."+str(prec)+"f}"
    if dollar_sign == False:
        fmt.replace("$", "", 1)
    return fmt.format(value)


def jinja2_datetime(date, locale="en"):
    return babel.dates.format_date(date, locale=locale)


os.environ['S3_USE_SIGV4'] = "1"
app = Flask(__name__)
#
# get settings
#
if "DEVELOPMENT" in sys.argv:
    app.config.from_object('flask-settings.DevelopmentConfig')
    print("DEVELOPMENT mode instance.")
else:
    app.config.from_object('flask-settings.ProductionConfig')
    print("PRODUCTION mode instance.")
#
# apply libraries
#
bcrypt = Bcrypt(app)

csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)

app.jinja_env.filters['escapejs'] = jinja2_escapejs_filter
app.jinja_env.filters['category_icon'] = jinja2_category_icon_filter
app.jinja_env.filters['creole_top'] = jinja2_creole_top
app.jinja_env.filters['USD'] = jinja2_USD
app.jinja_env.filters['datefmt'] = jinja2_datetime

qrcode = QRcode(app)

db = MongoEngine()
db.init_app(app)

oauth = OAuth()
google = oauth.remote_app(
    'google',
    app_key="GOOGLE_OAUTH"
)
oauth.init_app(app)


with open("static/img/nav-icon.svg") as nav_icon_file:
    nav_icon = nav_icon_file.read()

from login_handler import *
from views import *

if __name__ == '__main__':
    app.debug = app.config['DEBUG']
    app.run(host=app.config['HOST'], port=app.config['PORT'])

# eof
