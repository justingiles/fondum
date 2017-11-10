import random
import mongoengine as db
import msg

import account__models as models

#######################################
#
#    ACCOUNT
#
#######################################

def create_account(user):
    account = models.Account()
    account.ref_user = user
    account.s_number_name = str(random.randint(1000000, 9999999))
    account.save()
    return account


def read_account_byNumber(number):
    try:
        account = models.Account.objects.get(s_number_name=number)
    except db.DoesNotExist:
        return msg.err("Cannot find account {}".format(number))
    return account


def read_account_byUser(user):
    try:
        account = models.Account.objects.get(ref_user=user.id)
    except db.DoesNotExist:
        return msg.err("Cannot find account {}".format(user.id))
    return account
