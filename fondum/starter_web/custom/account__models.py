import mongoengine as db


class Account(db.Document):
    ref_user = db.ReferenceField("User", required=True)
    s_name = db.StringField()

