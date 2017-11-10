from wtforms import StringField, SelectField, FileField, PasswordField,\
    SubmitField, HiddenField, DateTimeField, IntegerField
from wtforms.validators import InputRequired
from flask import url_for, Response
from app import g, google
import msg
from page import Page, PageForm, PageTable
import account__database as database



# /account/new/
class New(Page):

    default_text = """
== Create New Account
"""

    class MainForm(PageForm):
        submit = SubmitField("Login With Google to Start Account")

        def process_form(self, wtf):
            return google.authorize(callback=url_for('google_authorized', est="new", _external=True))


# /account/login/
class Login(Page):

    default_text = """
== Login
"""

    class MainForm(PageForm):
        submit = SubmitField("Login With Google")

        def process_form(self, wtf):
            return google.authorize(callback=url_for('google_authorized', est="current", _external=True))

