from wtforms import StringField, SelectField, FileField, SubmitField, DateTimeField, IntegerField
from wtforms.validators import InputRequired, NumberRange
from app import g
import msg
from page import Page, PageForm, PageTable, DisplayPictureField, DisplayTextField


# /main/about/
class About(Page):

    default_text = """
==About {{DOMAIN}}

"""

