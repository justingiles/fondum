import mongoengine as db

NUMBER_WORDS = [
    "Zero",
    "One",
    "Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine"
]

class Account(db.Document):
    ref_user = db.ReferenceField("User", required=True)

    s_number_name = db.StringField(required=True)

    @property
    def display(self):
        first_name = NUMBER_WORDS[int(self.s_number_name[0])]
        last_name = NUMBER_WORDS[int(self.s_number_name[1])]
        middle_name = self.s_number_name[2:]
        return '{} "{}" {}'.format(first_name, middle_name, last_name)
