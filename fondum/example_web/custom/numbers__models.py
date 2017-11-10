import mongoengine as db
import datetime


class WonderfulNumber(db.Document):
    n_number = db.IntField(required=True)

    dt_posted = db.DateTimeField(required=True, default=datetime.datetime.now)
    n_likes = db.IntField(required=True, default=0)
    ref_posting_account = db.ReferenceField("Account")


class NumbersPostedByAccount(db.Document):
    ref_account = db.ReferenceField("Account")

    arr_numbers = db.ListField(db.ReferenceField("WonderfulNumber"))


class NumbersLikedByAccount(db.Document):
    ref_account = db.ReferenceField("Account")

    arr_likes = db.ListField(db.ReferenceField("WonderfulNumber"))


class TopNumbersList(db.Document):
    key = db.StringField()
    arr_numbers = db.ListField(db.ReferenceField("WonderfulNumber"))


# becasue of the MongoDB document size limit, tracking is stored
# as a very large number of small documents, rather than one big
# document per number.
#
class NumberLikeTracking(db.Document):
    n_number = db.IntField(required=True)
    ref_account = db.ReferenceField("Account")
