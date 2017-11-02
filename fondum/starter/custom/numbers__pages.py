from wtforms import StringField, SelectField, FileField, SubmitField, DateTimeField, IntegerField, HiddenField
from wtforms.validators import InputRequired, NumberRange
from app import g
import msg
from page import Page, PageForm, PageTable, DisplayPictureField, DisplayTextField
import numbers__database as database


# /numbers/top/
class Top(Page):

    default_text = """
==Top Numbers

All numbers are great and solve all known number-related problems.

But these numbers are especially numbery in nature.
"""

    class MostLiked(PageTable):

        key_name = "mostliked"
        table_name = "Most Liked"

        class LikedNumberRow(PageForm):
            n_number = IntegerField("Number")
            n_likes = IntegerField("Likes")
            posted_by = StringField("Posted By")

        def process_table(self, person=None, **kwargs):
            number_list = database.read_topNumbersList("most_liked")
            self.set_header(self.LikedNumberRow())
            for row in number_list.arr_numbers:
                r = self.LikedNumberRow()
                r.pull_data(row)
                r.n_number.url = "/numbers/detail/{}".format(r.n_number.data)
                r.posted_by.data = row.ref_posting_account.display
                r.posted_by.url = "/account/numbers/{}".format(row.ref_posting_account.s_number_name)
                self.rows.append(r)

    table_order = [
        MostLiked
    ]


# /numbers/post/
class Post(Page):

    login_required = True

    default_text = """
== Reverently Enter a New Number

If, with cunning and great thought, you have spawned a new number in your Mind. Please post it here.
"""

    class MainForm(PageForm):
        n_number = IntegerField("Number", validators=[
            InputRequired(),
            NumberRange(0, 2147483647)
        ])
        submit = SubmitField("Post Number")

        def process_form(self, wtf):
            result = database.create_number(wtf)
            if msg.is_bad(result):
                return result
            return msg.success("Posted {} to the world. That number is now known!".format(result.n_number))



# /numbers/detail/<number>
class Detail__number(Page):

    default_text = """
== All the details about this number.
"""

    class MainForm(PageForm):
        n_number = DisplayTextField("Number")
        n_likes = DisplayTextField("Likes")
        poster = DisplayTextField("Who Posted")
        dt_posted = DisplayTextField("Date Posted")
        number = HiddenField("number")
        like = SubmitField("Like!")

        def set_starting_values(self, number=None):
            number = database.read_number(number)
            self.pull_data(number)
            self.number.data = number.n_number
            self.poster.data = number.ref_posting_account.display

        def process_form(self, wtf, **kwargs):
            result = database.update_number_withLike(wtf)
            return result


# /numbers/search/
class Search(Page):

    default_text = """
== Find a number.
"""

    class MainForm(PageForm):
        n_number = IntegerField("Number", validators=[
            InputRequired(),
            NumberRange(0, 2147483647)
        ])
        submit = SubmitField("Search")

        def process_form(self, wtf, **kwargs):
            number = database.read_number(wtf.n_number.data)
            if msg.is_bad(number):
                return number
            return msg.success(
                "Number found. {} posted it.".format(number.ref_posting_account.display),
                return_def = "page_numbers_detail",
                number=str(number.n_number)
            )

# /numbers/about
class About(Page):

     default_text = """
== All About Numbers

//"...and then god Hermes decided that mankind needed a means of tracking the number of beasts that would need sacrificing. He strummed his lyre and from it notes fell in patterns. And lo, the peoples eyes widenned as they realized they could count those notes."//

Sadly, the ancient Greeks then took this number system and decide to write numbers with a bunch of "I", "V", "X" and other silliness. Still, the power of numbers began.

**This website celebrates numbers.**

PLease note that some numbers are NSFW due to their extreme numberiness.

"""