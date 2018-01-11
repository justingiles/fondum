import flask
import babelfish

#################################
#
#   Flask Messaging/Flash Support Functions
#
#################################

DEFAULT = 0
SUCCESS = 1
INFO = 2
WARNING = 3
DANGER = 4

MSG_FLASK_CAT = {
    DEFAULT: "message",
    SUCCESS: "success",
    INFO: "info",
    WARNING: "warning",
    DANGER: "danger"    
}
FLASK_CAT_LIST = ["message", "success", "info", "warning", "danger"]    

MSG_BACKGROUND = {
    DEFAULT: "DarkBlue",
    SUCCESS: "Green",
    INFO: "Aqua",
    WARNING: "Yellow",
    DANGER: "DarkRed"
}

MSG_FOREGROUND = {
    DEFAULT: "White",
    SUCCESS: "White",
    INFO: "White",
    WARNING: "Black",
    DANGER: "White"
}

# flash levels:
#
LOG_ONLY = 0   # send to logs, if logs are stored, but not to end-user
DISPLAY = 1    # show to end-user; this is the default level
ERROR = 2      # this is an error that should be looked at eventually
SECURITY = 3   # security exception! this type of error should never normally happen


class FlashEvent(object):
    def __init__(self):
        self.message = ""
        self.event_type = DEFAULT
        self.level = DISPLAY
        self.return_def = None
        self.return_def_parms = {}
        self.flash_event = True

    def __repr__(self):
        return "<FlashEvent type={} level={}>".format(
            MSG_FLASK_CAT[self.event_type],
            self.level
        )


def is_msg(test_object):
    if isinstance(test_object, FlashEvent):
        return True
    return False


def msg(msg, level=DISPLAY, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DEFAULT
    fe.level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def note(msg, level=LOG_ONLY, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DEFAULT
    fe.level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def success(msg, level=DISPLAY, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = SUCCESS
    fe.level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def info(msg, level=DISPLAY, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = INFO
    fe.level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def warning(msg, level=DISPLAY, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = WARNING
    fe.level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


# something went wrong but it is a normal kind of wrong. A user typing in a wrong
# password or using incorrect data in a field would generate an err. That is,
# having an 'err' occur is fully expected. The user simply needs to know that the
# operation failed.
def err(msg, level=DISPLAY, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DANGER
    fe.level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe

def error(*args, **kwargs):
    return err(*args, **kwargs)

#
# used to return events that shouldn't ever really happen. i.e. a software bug
def bug(msg, level=ERROR, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DANGER
    fe.level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe

# this is used to return events that indicate a possible security breach. Often
# used when checking for conditions that should be impossible to happen.
# a good example: a honey-pot URL was accessed. This is an obscure URL that is never
# linked to. So, without access to source code, it should be impossible to know
# that the URL exists at all. So, an outsider accessing it ISNT a bug per se. But it
# is a serious security warning.
#
def security(msg, level=SECURITY, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DANGER
    fe.level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe

def is_flashEvent(flash_event):
    if isinstance(flash_event, FlashEvent):
        return True
    if hasattr(flash_event, "flash_event"):
        return flash_event.flash_event
    return False

def is_msg(flash_event):
    return is_flashEvent(flash_event)

def is_good(flash_event, noneOkay=False):
    if is_flashEvent(flash_event):
        if flash_event.event_type == DANGER:
            return False
        if flash_event.level in [ERROR, SECURITY]:
            return False
        return True
    if (flash_event is None) and not noneOkay:
        return False
    return True

def is_bad(flash_event, noneOkay=False):
    return not is_good(flash_event, noneOkay = noneOkay)

def flash(msg, t=None):
    if is_flashEvent(msg):
        flask.flash(msg.message, MSG_FLASK_CAT[msg.event_type])
    else:
        event_type = "message"
        if t in FLASK_CAT_LIST:
            event_type = t
        flask.flash(str(msg), "message")
    return

COUNTRIES = sorted([(code, code+" - "+babelfish.COUNTRIES[code]) for code in babelfish.COUNTRIES])
COUNTRIES.insert(0, ("US", "US - UNITED STATES"))
