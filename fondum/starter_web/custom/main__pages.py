from wtforms import StringField, SelectField, FileField, SubmitField, DateTimeField, IntegerField
from wtforms.validators import InputRequired, NumberRange
from app import g
import msg
from page import Page, PageForm, PageTable, DisplayPictureField, DisplayTextField

from flask import render_template, render_template_string

# /main/about/
class About(Page):

    default_text = """
==About {{DOMAIN}}
"""


# /main/special/
class Special(Page):

    # a "fondum_bypass" method, if defined, causes fondum to basically ignore
    # _almost_ everything about Page and use fondum_pypass to render the web page instead.
    #
    # Do NOT use decorators. The route decorator is already handled by fondum compilation.
    # For the decorator requiring login, add/modify the "login_required" attribute.

    login_required = False

    def fondum_bypass(self, **kwargs):
        special_text = """
            <html>
              <body>
                <h1>Aha, {{g.display_name}}!</h1>
                We are running a hardcore "view" of our own!
                <p>
                Fancier:
                </p>
                <ul>
                   {% for x in short_list %}
                   <li><a href="/main/special-with-parm/{{x}}">{{x}}</li>
                   {% endfor %}
                </ul>
              </body>
            </html>
        """
        return render_template_string(special_text, short_list=["one", "two"])


# /main/special-with-parm/<myparm>
class SpecialWithParm__myparm(Page):

    # an example "fondum bypass" that has a route paramater (/main/special-with-parm/<myparm>)
    # this example also uses an html jinja file in the templates directory

    login_required = False

    def fondum_bypass(self, **kwargs):
        return render_template("special-with-parm.html", kwargs=kwargs)
