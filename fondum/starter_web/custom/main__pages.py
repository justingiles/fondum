from wtforms.validators import InputRequired, NumberRange
from app import g
import msg
from page import Page, PageForm, PageTable, \
    DisplayPictureField, DisplayTextField, ButtonUrlField, \
    BooleanField, DateField, DateTimeField, DecimalField, FileField, \
    FloatField, IntegerField, RadioField, SelectField, \
    SelectMultipleField, SubmitField, StringField, \
    HiddenField, PasswordField, TextAreaField
from flask import render_template, render_template_string
import datetime
import random

# /main/about/
class About(Page):

    default_text = """
==About 123.test
"""

# url will be /main/example-of-everything/
class ExampleOfEverything(Page):

    default_text = """
== Example of Everything

This very-crowded page is an example of all the items can be found on a "Page" class page.

They are (in order):

# Page Document (this section)
** Currently showing //default_text//, but can be overwritten with MongoDB document
# A Form
** a.k.a. //MainForm//
** "horizontal" form_style was chosen.
** a //process_form// function was found in the MainForm, so the 
# A Catalog
** TBD
# A Set of Tables
** Two tables; the first one has randomized data in it.


"""

    form_style = "horizontal"

    class MainForm(PageForm):

        b = BooleanField("My Boolean")
        d = DateField("My Date")
        dt = DateTimeField("My DateTime")
        fl = FloatField("My Float")
        i = IntegerField("My Integer")
        r = RadioField("My Radio", choices=[("x", "X"), ("y", "Y")], default="y")
        sf = SelectField("My Select", choices=[("a", "A"), ("b", "B")])
        sfm = SelectMultipleField("My Multiple Select", choices=[("c", "C"), ("d", "D")])
        s = StringField ("My String")
        h = HiddenField("My Hidden")
        p = PasswordField("My Password")
        t = TextAreaField("My Text Data")
        buf = ButtonUrlField("My Button Url Field", href="https://google.com")
        dpf = DisplayPictureField(
            "My Picture",
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/The_Earth_seen_from_Apollo_17.jpg/225px-The_Earth_seen_from_Apollo_17.jpg",
            href="https://www.yahoo.com"
        )
        dtf = DisplayTextField("My Displayed Text", default="abcdefg")
        submit = SubmitField("Send It")

        def set_starting_values(self, **kwargs):
            self.dt.data = datetime.datetime.now()
            self.t.data = "Some starting text!\n...and some more!"

        def process_form(self, wtf, **kwargs):
            #
            # this is where any database processing would happen
            #
            msg.flash("Got it! string={}, integer={}, etc.".format(wtf.s.data, wtf.i.data))
            return msg.success("All good.", return_def="page_main_about")




    class MyTableOne(PageTable):
        key_name = "tab_one"
        table_name = "My Table with Random Values"

        class MTRow(PageForm):
            b = BooleanField("My Boolean")
            d = DateField("My Date")
            dt = DateTimeField("My DateTime")
            fl = FloatField("My Float")
            i = IntegerField("My Integer")
            r = RadioField("My Radio", choices=[("x", "X"), ("y", "Y")], default="y")
            sf = SelectField("My Select", choices=[("a", "A"), ("b", "B")])
            sfm = SelectMultipleField("My Multiple Select", choices=[("c", "C"), ("d", "D"), ("e", "E"), ("f", "F")])
            s = StringField ("My String")
            h = HiddenField("My Hidden")
            p = PasswordField("My Password")
            t = TextAreaField("My Text Data")
            buf = ButtonUrlField("My Button Url Field", href="https://google.com")
            dpf = DisplayPictureField(
                "My Picture",
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/The_Earth_seen_from_Apollo_17.jpg/225px-The_Earth_seen_from_Apollo_17.jpg",
                href="https://www.yahoo.com"
            )
            dtf = DisplayTextField("My Displayed Text", default="abcdefg")
            submit = SubmitField("Send It")

        def process_table(self, **kwargs):
            self.set_header(self.MTRow())
            for n in range(1, 5):
                r = self.MTRow()
                r.b.data = random.choice([True, False])
                r.d.data = datetime.datetime.now()
                r.dt.data = datetime.datetime.now()
                r.fl.data = random.random()
                r.i.data = random.randint(-1000, 1000)
                r.r.data = random.choice(r.r.choices)[0]
                r.sf.data = random.choice(r.sf.choices)[0] # it does NOT display 'default'; it displays 'data'
                r.sfm.data = [random.choice(r.sfm.choices)[0], random.choice(r.sfm.choices)[0]]
                # r.sfm.data = [k for k,v in random.choices(r.sfm.choices, k=random.randint(0,len(r.sfm.choices)))]
                r.s.data = random.choice(["hat", "apple", "ball", "fish"])
                r.h.data = "you can't see me."
                r.p.data = "still can't see me."
                r.t.data = "line1\nline2\nline3\n"
                # r.buf.data = x  # it does not matter what 'data' contains
                # r.dpf.data = x
                self.rows.append(r)
            return msg.success("random number of rows of things.")

    class MyTableTwo(PageTable):
        key_name = "tab_two"
        table_name = "My Table Two"

        class TabTwoRow(PageForm):
            s_name = StringField("Name")
            s_something = StringField("Something")
            s_none = StringField("Nothing")

        def process_table(self, **kwargs):
            self.set_header(self.TabTwoRow())
            for a in ["a", "b", "c"]:
                r = self.TabTwoRow()
                r.s_name.data = a
                r.s_something.data = "blah"
                self.rows.append(r)
            return msg.success("rows of stuff for table 2.")


    table_order = [
        MyTableOne,
        MyTableTwo
    ]






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
