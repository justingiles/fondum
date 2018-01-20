from wtforms.validators import InputRequired, NumberRange
from app import g
import msg
from page import Page, PageForm, PageTable, \
    DisplayPictureField, DisplayTextField, ButtonUrlField, \
    BooleanField, DateField, DateTimeField, DecimalField, FileField, \
    FloatField, IntegerField, RadioField, SelectField, \
    SelectMultipleField, SubmitField, StringField, \
    HiddenField, PasswordField, TextAreaField
from flask import render_template, render_template_string, redirect
import datetime
import random
from sendmail import sendmail
import fondum_utility


# /example/about/
class About(Page):

    default_text = """
==About def.test
"""


def mylookup():
    return [("aa", "Dynamic A"), ("bb", "Dynamic B")]


# url will be /example/example-of-everything/
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
        sf = SelectField("My Select", choices=mylookup)
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

        def set_field_values(self, new_page, **kwargs):
            self.dt.data = datetime.datetime.now()
            self.t.data = "Some starting text!\n...and some more!"

        def process_form(self, wtf, **kwargs):
            #
            # this is where any database processing would happen
            #
            msg.flash("Got it! string={}, integer={}, etc.".format(wtf.s.data, wtf.i.data))
            return msg.success("All good.", return_def="page_example_about")




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






# /example/special/
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
                   <li><a href="/example/special-with-parm/{{x}}">{{x}}</li>
                   {% endfor %}
                </ul>
              </body>
            </html>
        """
        return render_template_string(special_text, short_list=["one", "two"])


# /example/special-with-parm/<myparm>
class SpecialWithParm__myparm(Page):

    # an example "fondum bypass" that has a route paramater (/example/special-with-parm/<myparm>)
    # this example also uses an html jinja file in the templates directory

    login_required = False

    def fondum_bypass(self, **kwargs):
        return render_template("special-with-parm.html", kwargs=kwargs)


# /example/example-sendmail/
class ExampleSendmail(Page):

    default_text = """
==== Examples of Extended Features
== Sendmail

The example below shows the //sendmail// feature of fondum. By default, this 
extended feature is turned off.

The example is kind of silly. Generally, one would never allow the general public
to send emails. It is strictly for demonstraction. In practice, you would use the function
more subtley and with greater restrictions.

** Currently uses //sendgrid// commercial service; which includes a free tier.
"""

    class MainForm(PageForm):

        msg_to = DisplayTextField("To:")
        msg_from = StringField("From:")
        msg_subject = StringField("Subject:")
        msg_text = TextAreaField("Body (with creole markup):")
        submit = SubmitField("Send An Email")

        def set_field_values(self, new_page, **kwargs):
            self.msg_to.data = "test@example.com"

        def process_form(self, wtf, **kwargs):
            #
            # this is where any database processing would happen
            #
            result_msg = sendmail(
                1,
                to_addr="test <test@example.com>",
                creole_text=self.msg_text.data, 
                subject=self.msg_subject.data, 
                from_addr=self.msg_from.data,
            )
            return result_msg


# /example/flash
class Flash(Page):

    default_text = """
== Example of Flash Messaging

Using the form below, enter a message and category of message and press Submit.
A copy of that message will then flash on the page after submission.
"""

    class MainForm(PageForm):

        message = StringField("Message content")
        category = SelectField("Category", choices=[
            ("message", "Default/Generic [message]"),
            ("success", "Success [success]"),
            ("info", "Informational [info]"),
            ("warning", "Warning/Caution [warning]"),
            ("danger", "Danger/Error/Failure [danger]"),
        ])
        submit = SubmitField("Submit")

        def process_form(self, wtf, **kwargs):
            #
            # this is where any database processing would happen
            #

            m = msg.message(self.message.data)
            m.set_category(self.category.data)
            return m


# NOTE: Normally the following would be stored in the corresponding
# 'x__models.py' file. So, in this case, it would be stored in
# 'examples__models.py'. But I break the normal rule here to help with
# documentation of this CopyFields example.
#

import mongoengine as db


class TestDocument(db.Document):
    name = db.StringField(label="Full Name", required=True)
    height = db.IntField(required=True)
    age = db.IntField()
    hair_color = db.StringField(
        choices=('black', 'brown', 'blond', 'red', 'grey'),
    )
    handedness = db.StringField(
        label = "Left/Right Handed",
        choices=('left', 'right'),
        radio=True
    )
    shirt_color = db.StringField(
        label="Shirt Color Assigned",
        default="blue",
        display_only=True,
    )
    notes = db.StringField(
        textarea=True
    )
    silly = db.StringField(
        label="Can't See Me",
        default="blimey",
        required=True,
        hide=True
    )
    income = db.FloatField(required=True)

#
# "extra" labels supported:
#    label = Field Label

# NOTE: Normally the following would be stored in the corresponding
# 'x__database.py' file. So, in this case, it would be stored in
# 'examples__database.py'. But I break the normal rule here to help with
# documentation of this CopyFields example.
#

from fondum_utility import copy_fields


def create_testDocument(wtf):
    doc = TestDocument()
    copy_fields(src=wtf, dest=doc)
    doc.save()
    return msg.success('Created TestDocument "{}"'.format(doc.name))


def read_testDocument(doc_id):
    doc = TestDocument.objects(id=doc_id).first()
    if doc:
        return doc
    return msg.err("Unable to locate document")


def readlist_testDocument_all():
    tdl = TestDocument.objects()
    return tdl


def delete_testDocument(doc_id):
    doc = read_testDocument(doc_id)
    if msg.is_message(doc):
        return doc
    doc.delete()
    return msg.success("TestDocument document deleted.")


# /example/copy-fields
class CopyFields(Page):

    default_text = """
== Example of the Copy Fields Function
===List Documents

"Fields" are importable in both directions.
* One can import the fields of a MongoEngine Document into a PageForm (child of WTForms) with the '_import_fields=obj' class variable.
* One can export the fields of PageForms into a MongoEngine Document with the 'fondum_utility.copy_fields(...)' function.

See the corresponding source code for this page for the example of use.

NOTE: By definition, '_import_fields' skips the 'id' fields or any field starting with an underscore.

NOTE: the library 'Flask-MongoEngine' also has a 'model_form' function that has function similar to '_import_fields'.

This particular page reads the contents of the 'TestDocument' collection and shows the entries.
"""

    class TableOne(PageTable):
        key_name = "main"
        table_name = ""  # an empty table name (and only one table) suppresses the tabs

        class Row(PageForm):
            _import_fields = TestDocument
            # _field_order is strictly optional; without it, the imports are simply appended
            delete = ButtonUrlField("Delete")
            _field_order = ['name', 'age', 'height', 'hair_color', 'shirt_color', 'notes', "handedness", "silly", 'income', "delete"]

        class CreateButtonRow(PageForm):
            create = ButtonUrlField("Create", href="/example/copy-fields-new/")

        def process_table(self, **kwargs):
            self.set_header(self.Row())
            tdl = readlist_testDocument_all()
            for doc in tdl:
                r = self.Row()
                fondum_utility.copy_fields(src=doc, dest=r)
                r.delete.href = "/example/copy-fields-delete/{}/".format(doc.id)
                self.rows.append(r)
            self.rows.append(self.CreateButtonRow())
            return msg.success("all documents")

    table_order = [
        TableOne,
    ]

# /example/copy-fields-new
class CopyFieldsNew(Page):

    default_text = """
== Example of the Copy Fields Function
=== Create New Record

This particular page creates a new document in the TestDocument collection.
"""

    class MainForm(PageForm):

        age = IntegerField("Current Age")
        submit = SubmitField("Submit")
        # _import_fields = models.TestDocument
        _import_fields = TestDocument

        # _field_order is strictly optional; without it, the imports are simply appended
        _field_order = ['name', 'age', 'height', 'hair_color', 'shirt_color', 'income', 'notes', 'silly', 'handedness', 'submit']

        def process_form(self, wtf, **kwargs):
            # return database.create_testDocument()
            response = create_testDocument(wtf)
            if msg.is_good(response):
                response.return_def = "page_example_copy_fields"
            return response

        def set_field_values(self, new_page, **kwargs):
            if new_page:
                self.age.data = 22


# /example/copy-fields-delete/<id>
class CopyFieldsDelete__id(Page):

    def fondum_bypass(self, **kwargs):
        doc_id = kwargs["id"]
        response = delete_testDocument(doc_id)
        msg.flash(response)
        return redirect("/example/copy-fields/")

# eof
