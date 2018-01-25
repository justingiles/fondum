from wtforms.validators import InputRequired
from flask_wtf import FlaskForm
from flask import send_file
from app import g
import msg
from page import (
    Page,
    PageForm,
    PageTable,
    DisplayPictureField,
    DisplayTextField,
    StringField,
    SelectField,
    FileField,
    SubmitField,
    TextAreaField,
    HiddenField,
    DateTimeField,
    DecimalField,
    FormField,
    BooleanField,
    ButtonUrlField
)
import admin__database as database
import admin__models as models
from s3 import s3_upload
import datetime
from decimal import Decimal
import zipfile
import io
from fondum_utility import copy_fields


# /admin/main
class Main(Page):

    admin_required = True

    default_text = """
== Admin Page

[[/admin/download-articles|Download Article Archive]]
[[/admin/logs|View Error Logs]]

[[/admin/article/new/|Create New Article]]
[[/admin/picture/new/|Upload New Picture]]
[[/admin/product/new/|Create New Catalog Product]]
    """

    class Articles(PageTable):
        key_name = "articles"
        table_name = "Page Articles"

        class ArticleRow(PageForm):
            s_key = StringField("URL Key")
            s_title = StringField("Title")
            tf_blog = BooleanField("Blog Entry?")
            delete_function = ButtonUrlField("Delete")

        def process_table(self, **kwargs):
            article_list = database.read_articleList(list_type="all")
            self.set_header(self.ArticleRow())
            for a in article_list.arr_articles:
                r = self.ArticleRow()
                copy_fields(src=a, dest=r)
                ukey = "_".join(a.s_key.split("/"))
                r.s_key.href = "/admin/article/{}".format(ukey)
                r.delete_function.href = "/admin/article-delete/{}".format(ukey)
                self.rows.append(r)
            return msg.success("Articles.")

    class Pictures(PageTable):
        key_name = "pictures"
        table_name = "Article Pictures"

        class PictureRow(PageForm):
            s_key = StringField("Key Name")
            usage_url = StringField("Creole Usage")
            dt_uploaded = DateTimeField("Date Uploaded")

        def process_table(self, **kwargs):
            pic_list = database.readlist_articlePictures()
            self.set_header(self.PictureRow())
            for p in pic_list:
                r = self.PictureRow()
                copy_fields(dest=r, src=p)
                r.s_key.href = "/admin/picture/{}".format(r.s_key.data)
                r.usage_url.data = "/apic/{}.png".format(r.s_key.data)
                self.rows.append(r)
            return msg.success("Pictures.")

    class Products(PageTable):
        key_name = "products"
        table_name = "Catalog Products/Listings"

        class ProductRow(PageForm):
            s_key = StringField("Key Name / SKU")
            s_title = StringField("Title")
            categories = StringField("Categories")
            delete_function = ButtonUrlField("Delete")

        def process_table(self, pkey=None, **kwargs):
            product_list = database.readlist_product(categories=[])
            self.set_header(self.ProductRow())
            for a in product_list:
                r = self.ProductRow()
                copy_fields(dest=r, src=a)
                r.s_key.href = "/admin/product/{}".format(a.s_key)
                r.categories.data = ", ".join(a.arr_categories)
                r.delete_function.href = "/admin/product-delete/{}".format(a.s_key)
                self.rows.append(r)
            return msg.success("Products.")

    table_order = [
        Articles,
        Pictures,
        Products
    ]


# /admin/article/<pkey>
class Article__pkey(Page):

    admin_required = True

    default_text = """
== Admin
=== Article Edit/Create

[[/admin/main/|Return to Main]]
    """

    class MainForm(PageForm):

        class BloggerDetail(PageForm):
            tf_blog = BooleanField("Blog article?", description="check if true")
            s_blogger_name = StringField("Author")
            dt_blog_date = DateTimeField("Date (YYYY-MM-DD HH:MM:SS)")
            s_byline = StringField("By-Line", description="A short one-line description that adds to the title.")
            s_img_key = StringField("Small Image Key")
            categories = StringField("Categories", description="comma-delimited list")

        group_name = StringField("Group Name")
        page_name = StringField("Page Name")
        s_title = StringField("Title")
        s_creole_text = TextAreaField("Text (creole 1.0 format)")
        blog = FormField(BloggerDetail, "For articles that are also blogs...")
        submit = SubmitField("Update")

        def process_form(self, wtf, pkey=None):
            group_name = wtf.group_name.data
            page_name = wtf.page_name.data
            key = database.build_key(group_name, page_name)
            result = database.upsert_article(key, wtf)
            if msg.is_good(result):
                return msg.success('Article saved.')
            return result

        def set_field_values(self, new_page, pkey=None):
            if pkey == "new":
                self.blog.dt_blog_date.data = datetime.datetime.now()
                self.submit.label.text = "Create"
            else:
                (group_name, page_name) = pkey.split("_")
                true_key = database.build_key(group_name, page_name)
                article = database.read_article_byKey(true_key)
                self.pull_data(article)
                self.blog.pull_data(article)
                self.blog.categories.data = ", ".join(article.arr_blog_categories)
                self.group_name.data = group_name
                self.page_name.data = page_name


# /admin/article-delete/<pkey>
class ArticleDelete__pkey(Page):

    admin_required = True

    default_text = """
== Admin
=== Article Deletion

[[/admin/main/|Return to Main]]
    """

    class MainForm(PageForm):
        pkey = HiddenField()
        s_title = StringField("Title")
        s_creole_text = TextAreaField("Text (creole 1.0 format)")
        submit = SubmitField("DELETE")

        def process_form(self, wtf, **kwargs):
            true_key = wtf.pkey.data.replace("_", "/")
            result = database.delete_article(true_key)
            if msg.is_good(result):
                return msg.success('Article deleted.', return_def="page_admin_main")
            return result

        def set_field_values(self, new_page, pkey=None):
            true_key = pkey.replace("_", "/")
            article = database.read_article_byKey(true_key)
            if article:
                self.pull_data(article)
            self.pkey.data = pkey


# /admin/picture/<pkey>
class Picture__pkey(Page):

    admin_required = True

    default_text = """
== Admin
=== Upload Picture

[[/admin/main/|Return to Main]]
    """

    class MainForm(PageForm):
        s_key = StringField(
            "Key Name (short, no punctuation other than underscore)",
            validators=[InputRequired()]
        )
        file = FileField(u'PNG image file')
        s_etag = DisplayTextField('e-tag found on Amazon S3')
        s_notes = TextAreaField("Notes for internal reference")
        submit = SubmitField("Upsert Picture")

        def process_form(self, wtf, **kwargs):
            key = wtf.s_key.data.strip()
            if key == "new":
                return msg.err('Picture key cannot be "new".')
            if not key:
                return msg.err('Picture key name is required.')
            details = s3_upload(wtf.file)
            result = database.upsert_articlePicture(key, wtf, details)
            return result

        def set_field_values(self, new_page, pkey=None):
            pic = database.read_articlePicture(pkey)
            if pic:
                self.pull_data(pic)
                self.file = HiddenField("DO NOT USE")


# /admin/product/<pkey>
class Product__pkey(Page):

    admin_required = True

    default_text = """
== Admin
=== Edit/Insert Product

[[/admin/main/|Return to Main]]
"""

    class MainForm(PageForm):
        s_key = StringField(
            "Key Name or SKU (short, no punctuation other than underscore)",
            validators=[InputRequired()]
        )
        s_title = StringField("Title")
        s_made_by = StringField("Made By")
        fl_price = DecimalField("Price")
        s_shipping_detail = StringField("Shipping Detail")
        s_short_description = TextAreaField(
            "Short Description",
            description="(Creole 1.0)"
        )
        s_img_key = StringField("Image Key")
        s_url = StringField("Product Link (URL)")
        categories = StringField("Categories (seperate by comma)")
        submit = SubmitField("Upsert Product")

        def process_form(self, wtf, **kwargs):
            key = wtf.s_key.data.strip()
            if key == "new":
                return msg.err('Product key/sku cannot be "new".')
            if not key:
                return msg.err('Picture key/sku name is required.')
            result = database.upsert_product(key, wtf)
            return result

        def set_field_values(self, new_page, pkey=None):
            if pkey == "new":
                self.fl_price.data = Decimal("0.00")
                return
            product = database.read_product(pkey)
            if product:
                self.pull_data(product)
                self.categories.data = ", ".join(product.arr_categories)


# /admin/product-delete/<pkey>
class ProductDelete__pkey(Page):

    admin_required = True

    default_text = """
== Admin
=== Product Deletion

[[/admin/main/|Return to Main]]
    """

    class MainForm(PageForm):
        s_key = DisplayTextField("Product Key / SKU")
        s_title = DisplayTextField("Title")
        s_short_description = DisplayTextField("Short Description")
        submit = SubmitField("DELETE")

        def process_form(self, wtf, pkey=None, **kwargs):
            result = database.delete_product(pkey)
            if msg.is_good(result):
                return msg.success('Product deleted.', return_def="page_admin_main")
            return result

        def set_field_values(self, new_page, pkey=None):
            product = database.read_product(pkey)
            if product:
                self.pull_data(product)


# /admin/logs
class Logs(Page):

    admin_required = True

    default_text = """
== Admin
=== Last 50 Log Entries

[[/admin/main/|Return to Main]]
    """

    class EventLogs(PageTable):
        key_name = "logs"
        table_name = "Event Logger"

        class LogRow(PageForm):
            _import_fields = models.Logs
            _field_order = [
                "dt_created",
                "s_event_type",
                "s_log_level", 
                "s_display_level",
                "s_instance",
                "s_src",
                "s_message",
                "s_logger_string",
            ]

        def process_table(self, **kwargs):
            log_list = database.readlist_log(qty=50)
            self.set_header(self.LogRow())
            for log in log_list:
                r = self.LogRow()
                copy_fields(src=log, dest=r)
                self.rows.append(r)
            return msg.success("Event Logs.")

    table_order = [
        EventLogs,
    ]


# /admin/download-articles
class DownloadArticles(Page):

    admin_required = True

    default_text = """
== Admin
=== Download Articles

[[/admin/main/|Return to Main]]

Downloading articles is a great way to make a backup of any article content of
your web site that is generated via the database.

The file itself is a simple ZIP archive of articles. They are stored as JSON
documents.

To use as the contents of your 'cache' directory. Simply unzip the file, and
copy the JSON documents into that directory.

[[/admin/download-articles/articles.zip|DOWNLOAD]]

NOTE: this download does NOT include any 'cache' or 'code' content. It is strictly
any web content that is stored in the MongoDB database.
    """



class ZipArticles(Page):  #%OVERRIDE_URL=/admin/download-articles/articles.zip

    admin_required = True

    def fondum_bypass(self, **kwargs):
        article_list = database.readlist_article_all()
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for article in article_list:
                data = zipfile.ZipInfo("{}.{}.json".format(
                    article.group_name, article.page_name
                ))
                if article.dt_last_update:
                    data.date_time = article.dt_last_update.timetuple()[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(data, str(article.to_json()))
        memory_file.seek(0)
        return send_file(memory_file, attachment_filename='articles.zip', as_attachment=True)


