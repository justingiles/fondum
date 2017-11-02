from PLOD import PLOD
import copy
import mongoengine as db
import numbers__models as models
import msg
from app import g

############################################
#
#    NUMBERS
#
############################################


def _save_number(number, new=False):
    number.save()
    if new:
        update_numbersPostedByAccount_withNewNumber(number)
    update_topNumberList_considerLikeCount(number)
    return


def create_number(wtf):
    da_digits = int(wtf.n_number.data)
    result = read_number(da_digits)
    if msg.is_good(result):
        return msg.err("The otherwise wonderful number {} has already been posted by {}.".format(
            da_digits,
            result.ref_posting_account.display
        ))
    number = models.WonderfulNumber()
    number.n_number = da_digits
    number.n_likes = 0
    number.ref_posting_account = g.account
    _save_number(number, new=True)
    return number


def read_number(number):
    number = int(number)
    try:
        n = models.WonderfulNumber.objects.get(n_number=number)
    except db.DoesNotExist:
        n = msg.err("Number {} not found.".format(number))
    except:
        n = msg.bug("Unknown error encountered")
    return n


def update_number_withLike(wtf):
    number = wtf.number.data
    n = read_number(number)
    if msg.is_bad(n):
        return n
    result = update_numbersLikedByAccount_withNewNumber(n, g.account)
    if msg.is_bad(result):  # prevents re-liking the same number
        return result
    result = update_numberLikeTracking_addLike(n, g.account)
    if msg.is_bad(result):
        return result
    n.n_likes += 1
    _save_number(n)
    return msg.success("You like {}.".format(number))


######################################
#
#    NUMBERS POSTED BY ONE ACCOUNT
#
######################################

def read_numbersPostedByAccount(account):
    try:
        np = models.NumbersPostedByAccount.objects.get(ref_account=account.id)
    except db.DoesNotExist:
        np = models.NumbersPostedByAccount()
        np.ref_account = account
        np.arr_numbers = []
        np.save()
    return np


def update_numbersPostedByAccount_withNewNumber(number):
    np = read_numbersPostedByAccount(number.ref_posting_account)
    if PLOD(np.arr_numbers).eq("n_number", number.n_number).found():
        return msg.bug("{} already posted by account".format(number.n_number))
    np.arr_numbers.append(number)
    np.save()
    return np


######################################
#
#    NUMBERS LIKED BY ONE ACCOUNT
#
######################################

def read_numbersLikedByAccount(account):
    try:
        nl = models.NumbersLikedByAccount.objects.get(ref_account=account.id)
    except db.DoesNotExist:
        nl = models.NumbersLikedByAccount()
        nl.ref_account = account
        nl.arr_numbers = []
        nl.save()
    return nl


def update_numbersLikedByAccount_withNewNumber(number, account):
    nl = read_numbersLikedByAccount(account)
    if PLOD(nl.arr_likes).eq("n_number", number.n_number).found():
        return msg.bug("You already like {}".format(number.n_number))
    nl.arr_likes.append(number)
    nl.save()
    return nl


#######################################
#
#    TOP NUMBER LISTS
#
#######################################

def read_topNumbersList(top_key):
    try:
        tnl = models.TopNumbersList.objects.get(key=top_key)
    except db.DoesNotExist:
        tnl = models.TopNumbersList()
        tnl.key = top_key
        tnl.arr_numbers = []
        tnl.save()
    return tnl


def update_topNumberList_considerLikeCount(number):
    tnl = read_topNumbersList("most_liked")
    if tnl.arr_numbers:
        threshold = tnl.arr_numbers[-1].n_likes
    else:
        threshold = 0
    if number.n_likes >= threshold:
        if PLOD(tnl.arr_numbers).eq('n_number', number.n_number).missing():
            tnl.arr_numbers.append(number)
            tnl.arr_numbers = PLOD(tnl.arr_numbers).sort("n_likes", reverse=True).returnList(limit=20)
            tnl.save()
    return tnl

#######################################
#
#    NUMBER LIKE TRACKING
#
#######################################

def update_numberLikeTracking_addLike(number, account):
    try:
        nl = models.NumberLikeTracking.objects.get(
            n_number=number.n_number,
            ref_account=account.id
        )
    except db.DoesNotExist:
        nl = None
    if nl is not None:
        return msg.err("Number is already liked by that account.")
    nl = models.NumberLikeTracking()
    nl.n_number = number.n_number
    nl.ref_account = account
    nl.save()
    return nl
