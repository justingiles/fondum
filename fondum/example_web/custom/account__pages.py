from wtforms import StringField, SelectField, FileField, PasswordField,\
    SubmitField, HiddenField, DateTimeField, IntegerField
from wtforms.validators import InputRequired
from flask import url_for, Response
from app import g, google
import msg
from page import Page, PageForm, PageTable
import account__database as database
import numbers__database



# /account/new/
class New(Page):

    default_text = """
== Create New Account

With a new account here, a huge new world of individual number appreciation-ness opens up to you.

Due to the simple person who wrote this web site, it is only possible to start your new account via Google.

Click on the button. It calls to you.
"""

    class MainForm(PageForm):
        submit = SubmitField("Login With Google to Start Account")

        def process_form(self, wtf):
            return google.authorize(callback=url_for('google_authorized', est="new", _external=True))


# /account/login/
class Login(Page):

    default_text = """
== Login

By logging in you can mark numbers as 'liked'. Life is complete.

The only way to log into your account is via Google. You encountered that when you first created your account.
"""

    class MainForm(PageForm):
        submit = SubmitField("Login With Google")

        def process_form(self, wtf):
            return google.authorize(callback=url_for('google_authorized', est="current", _external=True))


# /account/numbers/person
class Numbers__person(Page):


    default_text = """
== Person's Number Details

It is here that we can examine a person's true number(s).
"""


    class MainForm(PageForm):
        display = StringField("Number Name")
        s_number_name = StringField("(dull version)")

        def set_starting_values(self, person=None):
            if person=="me" and g.account:
                account = g.account
            else:
                account = database.read_account_byNumber(person)
            if msg.is_good(account):
                self.pull_data(account)
                self.display.data = account.display
            else:
                self.s_number_name.data = "Cannot Locate Account"


    class Numbers(PageTable):

        key_name = "mineminemine"
        table_name = "Posted Numbers"

        class PostedNumberRow(PageForm):
            n_number = IntegerField("Number")
            n_likes = IntegerField("Likes")
            dt_posted = DateTimeField("Date Posted")

        def process_table(self, person=None, **kwargs):
            if person=="me" and g.account:
                account = g.account
            else:
                account = database.read_account_byNumber(person)
            number_list = numbers__database.read_numbersPostedByAccount(account)
            self.set_header(self.PostedNumberRow())
            for row in number_list.arr_numbers:
                r = self.PostedNumberRow()
                r.pull_data(row)
                r.n_number.url = "/numbers/detail/{}/".format(r.n_number.data)
                self.rows.append(r)


    class Likes(PageTable):

        key_name = "liked"
        table_name = "Liked Numbers"

        class LikedNumberRow(PageForm):
            n_number = IntegerField("Number")
            n_likes = IntegerField("Likes")
            posted_by = StringField("Posted By")
 
        def process_table(self, person=None, **kwargs):
            if person=="me" and g.account:
                account = g.account
            else:
                account = database.read_account_byNumber(person)
            number_list = numbers__database.read_numbersLikedByAccount(account)
            self.set_header(self.LikedNumberRow())
            for row in number_list.arr_likes:
                r = self.LikedNumberRow()
                r.pull_data(row)
                r.posted_by.data = row.ref_posting_account.display
                r.posted_by.url = "/account/numbers/{}/".format(row.ref_posting_account.s_number_name)
                r.n_number.url = "/numbers/detail/{}/".format(r.n_number.data)
                self.rows.append(r)

    table_order = [
        Numbers,
        Likes
    ]



