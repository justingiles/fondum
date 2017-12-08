from flask_wtf import FlaskForm
import wtforms as w
from wtforms.validators import InputRequired
from app import g
import copy
import msg

import admin__database


class Page(object):

    login_required = False
    table_order = []
    default_text = None
    only_use_default_text = False
    use_jinja = True
    default_text_data = {"g": g}


    class Top(object):
        pass

    class Bottom(object):
        pass

    class Left(object):
        pass

    class Right(object):
        pass

    class Middle(object):
        pass

    def __init__(self):
        self.status = msg.error("page not processed")
        self.wtf = None
        # check for form
        if hasattr(self, "MainForm"):
            self.has_form = True
        else:
            self.has_form = False
            self.MainForm = None
        # check for tables
        if self.table_order:
            self.has_tables = True
        else:
            self.has_tables = False
        # check for catalog
        if hasattr(self, "MainCatalog"):
            self.has_catalog = True
        else:
            self.has_catalog = False


    def process(self, TABLE_NAME=None, **kwargs):
        self.url_params = kwargs
        #
        # PROCESS TABLES
        #
        if self.has_tables:
            self.current_table_name = None
            self.tables = []
            for table_class in self.table_order:
                self.tables.append(table_class(outer_page_instance=self))
            self.default_table_name = self.tables[0].key_name
            if not TABLE_NAME:
                TABLE_NAME = self.default_table_name
            self.table_name = TABLE_NAME
            self.status = msg.err("table name [{}] not found".format(self.table_name))
            self.skip_table_body = True
            for table in self.tables:
                if table.key_name == self.table_name:
                    self.display_table = table
                    self.status = table.process_table(**kwargs)  # should we add TABLE_NAME to start of params?
                    if not isinstance(self.status, EmptyTable):
                        self.skip_table_body = False
        #
        # PROCESS CATALOG
        #
        if self.has_catalog:
            self.catalog = self.MainCatalog(self)
            self.catalog.process_catalog(TABLE_NAME=TABLE_NAME, **kwargs)
        #
        # PROCESS MAIN FORM
        #
        if self.has_form:
            self.wtf = self.MainForm(outer_page_instance=self)
        #
        self.status = msg.success("page processed")


class PageForm(FlaskForm):

    def __init__(self, outer_page_instance=None, *args,  **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.page = outer_page_instance

    def pull_data(self, source):
        own_keys = [k.short_name for k in self]
        for key in source:
            if key in own_keys:
                self[key].data = source[key]

    def display_items(self):
        temp = []
        for field in self:
            if field.type in ["HiddenField", "CSRFTokenField"]:
                pass
            else:
                temp.append(field)
        return temp


class PageTable(object):

    key_name = "not defined"
    table_name = "Not Defined"

    def __init__(self, outer_page_instance=None):
        self.page = outer_page_instance
        self.rows = []
        self.header = None

    def set_header(self, page_form):
        self.header = page_form


class EmptyTable(object):
    pass


class PageProduct(object):

    def __init__(self, key):
        self.key = key
        self.title = ""
        self.made_by = None
        self.price = None
        self.shipping_detail = None
        self.short_description = None
        self.img_url = None


class PageCatalog(object):

    columns = 3
    use_table_name_as_category = False
    show_img = True
    show_made_by = True
    show_price = True
    show_shipping_detail = False
    show_short_description = True
    show_date = False
    pic_position = Page.Top

    def __init__(self, outer_page_instance):
        self.products = []
        self.page = outer_page_instance

    def process_catalog(self, categories=None, TABLE_NAME=None, **kwargs):
        if self.use_table_name_as_category:
            if TABLE_NAME == "*":
                categories = None
            elif TABLE_NAME:
                categories = [TABLE_NAME]
            else:
                categories = None
        self.products = admin__database.readlist_product(categories)
        return


class BlogCatalog(PageCatalog):

    columns = 2
    use_table_name_as_category = True
    show_img = True
    show_made_by = True
    show_price = False
    show_shipping_detail = False
    show_short_description = True
    show_date = True
    pic_position = Page.Left

    def process_catalog(self, categories=None, TABLE_NAME=None, **kwargs):
        if self.use_table_name_as_category:
            if TABLE_NAME == "*":
                categories = None
            elif TABLE_NAME:
                categories = [TABLE_NAME]
            else:
                categories = None
        blog_entries = admin__database.read_articleList_asProducts(list_type="blog")
        self.products = blog_entries
        return

########################################
#
#  NEW WTF-STYLE FIELDS
#
########################################

class DisplayPictureField(w.StringField):
    def __init__(self, label=None, validators=None, url=None, **kwargs):
        super(StringField, self).__init__(label=label, validators=validators, **kwargs)
        self.url = url
        self.data = url


class DisplayTextField(w.StringField):
    def __init__(self, label=None, validators=None, **kwargs):
        super(StringField, self).__init__(label=label, validators=validators, **kwargs)


class ButtonUrlField(w.StringField):
    def __init__(self, label=None, validators=None, href=None, **kwargs):
        super(StringField, self).__init__(label=label, validators=validators, **kwargs)

##########################################
#
#  NEW FEATURES FOR EXISTING WTFORMS FIELDS
#
##########################################

class BooleanField(w.BooleanField):
    def __init__(self, label=None, validators=None, href=None, **kwargs):
        super(BooleanField, self).__init__(label=label, validators=validators, **kwargs)


class DateField(w.DateField):
    def __init__(self, label=None, validators=None, href=None, **kwargs):
        super(DateField, self).__init__(label=label, validators=validators, **kwargs)


class DateTimeField(w.DateTimeField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d', href=None, **kwargs):
        super(DateTimeField, self).__init__(label=label, validators=validators, format=format, **kwargs)


class DecimalField(w.DecimalField):
    def __init__(self, label=None, validators=None, href=None, format='%Y-%m-%d %H:%M:%S', **kwargs):
        super(DecimalField, self).__init__(label=label, validators=validators, format=format, **kwargs)


class FileField(w.FileField):
    def __init__(self, label=None, validators=None, href=None, **kwargs):
        super(FileField, self).__init__(label=label, validators=validators, **kwargs)


# class MultipleFileField(w.MultipleFileField):
#     def __init__(self, label=None, validators=None, href=None, **kwargs):
#         super(MultipleFileField, self).__init__(label=label, validators=validators, **kwargs)


class FloatField(w.FloatField):
    def __init__(self, label=None, validators=None, href=None, **kwargs):
        super(FloatField, self).__init__(label=label, validators=validators, **kwargs)


class IntegerField(w.IntegerField):
    def __init__(self, label=None, validators=None, href=None, **kwargs):
        super(IntegerField, self).__init__(label=label, validators=validators, **kwargs)


class RadioField(w.RadioField):
    def __init__(self, label=None, validators=None, href=None, **kwargs):
        super(RadioField, self).__init__(label=label, validators=validators, **kwargs)


class SelectField(w.SelectField):
    def __init__(self, label=None, validators=None, coerce=w.compat.text_type, choices=None, href=None, **kwargs):
        super(SelectField, self).__init__(label=label, validators=validators, coerce=coerce, choices=choices, **kwargs)


class SelectMultipleField(w.SelectMultipleField):
    def __init__(self, label=None, validators=None, coerce=w.compat.text_type, choices=None, href=None, **kwargs):
        super(SelectMultipleField, self).__init__(label=label, validators=validators, coerce=coerce, choices=choices, **kwargs)


class SubmitField(w.SubmitField):
    def __init__(self, label=None, validators=None, href=None, **kwargs):
        super(SubmitField, self).__init__(label=label, validators=validators, **kwargs)


class StringField(w.StringField):
    def __init__(self, label=None, validators=None, href=None, **kwargs):
        super(StringField, self).__init__(label=label, validators=validators, **kwargs)


class HiddenField(w.HiddenField):
    def __init__(self, label=None, validators=None, href=None, **kwargs):
        super(HiddenField, self).__init__(label=label, validators=validators, **kwargs)


class PasswordField(w.PasswordField):
    def __init__(self, label=None, validators=None, href=None, **kwargs):
        super(PasswordField, self).__init__(label=label, validators=validators, **kwargs)


class TextAreaField(w.TextAreaField):
    def __init__(self, label=None, validators=None, href=None, **kwargs):
        super(TextAreaField, self).__init__(label=label, validators=validators, **kwargs)

