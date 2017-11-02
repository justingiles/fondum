from wtforms import StringField, SelectField, FileField, SubmitField, DateTimeField, IntegerField
from wtforms.validators import InputRequired, NumberRange
from app import g
import msg
from page import Page, PageForm, PageTable, DisplayPictureField, DisplayTextField


# /company/store/
class Store(Page):

    default_text = """
==Store to Buy Stuff

This part of jcfs does not actually do anything  yet.
"""


# /company/store/
class About(Page):

    default_text = """
==About [REDACTED] Company

This web site relies on the TCP/IP protocol. Unfortunately TCP/IP packet sequences must arrive in a manner dependent on the forward movement of time.

So, it is not really possible to correctly describe this company that does not yet exist. But when it does begin to exist, this company will be HUGE; which is even more impressive in the year 20[REDACTED].

Even pre-existance, this website has pretty much **captured** the full and complete **integer-liking marketplace**.

//note: some part of this document were/will be redacted per requirements of Linearization Entropy Oversight Committee.//
"""

