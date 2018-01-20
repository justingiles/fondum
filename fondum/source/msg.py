import flask
import babelfish
import logging


###################################
#
#    CONSTANTS
#
###################################

#
# DISPLAY CATEGORY TYPES
#
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
MSG_CAT_MAP = {
    "message": DEFAULT,
    "success": SUCCESS,
    "info": INFO,
    "warning": WARNING,
    "danger": DANGER,
}
FLASK_CAT_LIST = ["message", "success", "info", "warning", "danger"]    

# answers question, "is it good?"
MSG_CAT_JUDGEMENT = {
    DEFAULT: True,
    SUCCESS: True,
    INFO: True,
    WARNING: True,
    DANGER: False    
}

#
# LOGGING LEVELS
#
LOG_DESCRIPTION = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.WARNING: "WARNING",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRITICAL"
}

#
# PRESENTATION
#

DISP_NONE = 0             # don't display at all
DISP_SHOW = 1             # show to end-user; this is the default level; progress continues
DISP_ALERT = 2          # show to end-user; same as "display" but slightly more aggressive

DISP_DESCRIPTION = {
    DISP_NONE: "NONE",
    DISP_SHOW: "SHOW",
    DISP_ALERT: "WARNING",
}


#################################
#
#   LOGGING
#
#################################

class MongoHandler(logging.Handler):

    def emit(self, record):
        import admin__database
        record.formatted_message = self.format(record)
        admin__database.create_log_viaLoggingRecord(record)
        return True



#################################
#
#   Flask Messaging/Flash Support Functions
#
#################################

class FlashEvent(object):
    def __init__(self):
        self.message = ""
        self.event_type = DEFAULT
        self.display_level = DISP_SHOW
        self.log_level = logging.INFO
        self.return_def = None
        self.return_def_parms = {}
        self.flash_event = True

    def set_category(self, category):
        if category in MSG_CAT_MAP:
            self.event_type = MSG_CAT_MAP[category]

    def log(self):
        import admin__database
        admin__database.create_log_viaFlashEvent(self)
        return True

    def __repr__(self):
        return "<FlashEvent type={} level={}>".format(
            MSG_FLASK_CAT[self.event_type],
            self.display_level
        )


def is_msg(test_object):
    if isinstance(test_object, FlashEvent):
        return True
    return False

def is_message(test_object):
    return is_msg(test_object)


def msg(msg, display_level=DISP_SHOW, log_level=logging.INFO, return_def=None, **kwargs):
    if 'level' in kwargs:
        display_level = kwargs['level']
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DEFAULT
    fe.display_level = display_level
    fe.log_level = log_level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def message(*args, **kwargs):
    return msg(*args, **kwargs)


def note(msg, display_level=DISP_NONE, log_level=logging.INFO, return_def=None, **kwargs):
    if 'level' in kwargs:
        display_level = kwargs['level']
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DEFAULT
    fe.display_level = display_level
    fe.log_level = log_level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def success(msg, display_level=DISP_SHOW, log_level=logging.DEBUG, return_def=None, **kwargs):
    if 'level' in kwargs:
        display_level = kwargs['level']
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = SUCCESS
    fe.display_level = display_level
    fe.log_level = log_level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def info(msg, display_level=DISP_SHOW, log_level=logging.INFO, return_def=None, **kwargs):
    if 'level' in kwargs:
        display_level = kwargs['level']
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = INFO
    fe.display_level = display_level
    fe.log_level = log_level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def warning(msg, display_level=DISP_SHOW, log_level=logging.WARNING, return_def=None, **kwargs):
    if 'level' in kwargs:
        display_level = kwargs['level']
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = WARNING
    fe.display_level = display_level
    fe.log_level = log_level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


# something went wrong but it is a normal kind of wrong. A user typing in a wrong
# password or using incorrect data in a field would generate an err. That is,
# having an 'err' occur is fully expected. The user simply needs to know that the
# operation failed.
def err(msg, display_level=DISP_SHOW, log_level=logging.ERROR, return_def=None, **kwargs):
    if 'level' in kwargs:
        display_level = kwargs['level']
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DANGER
    fe.display_level = display_level
    fe.log_level = log_level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def error(*args, **kwargs):
    return err(*args, **kwargs)


def fail(*args, **kwargs):
    return err(*args, **kwargs)


def failure(*args, **kwargs):
    return err(*args, **kwargs)


#
# used to return events that shouldn't ever really happen. i.e. a software bug
def bug(msg, display_level=DISP_ALERT, log_level=logging.ERROR, return_def=None, **kwargs):
    if 'level' in kwargs:
        display_level = kwargs['level']
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DANGER
    fe.display_level = display_level
    fe.log_level = log_level
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
def security(msg, display_level=DISP_ALERT, log_level=logging.CRITICAL, return_def=None, **kwargs):
    if 'level' in kwargs:
        display_level = kwargs['level']
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DANGER
    fe.display_level = display_level
    fe.log_level = log_level
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
        # if flash_event.display_level in [DISP_ALERT]:
        #     return False
        return True
    if (flash_event is None) and not noneOkay:
        return False
    return True


def is_bad(flash_event, noneOkay=False):
    return not is_good(flash_event, noneOkay=noneOkay)


def flash(message, t=None, display_level=None, log_level=None):
    '''
    use 'flash' when you want the msg displayed to user.
    Either pass in a msg.<event> class instance.
    Or plass in a text message with parameters. The second parameter can be
    a string representations of the category.
    '''
    if not is_flashEvent(message):
        message = msg(str(message))
    #
    # adjust as needed
    #
    if display_level:
        message.display_level = display_level
    if log_level:
        message.log_level = log_level
    if t in MSG_CAT_MAP:
        message.event_type = MSG_CAT_MAP[t]
    #
    # actually display/log
    #
    if message.display_level != DISP_NONE:
        flask.flash(message.message, MSG_FLASK_CAT[message.event_type])
    message.log()
    #
    return


COUNTRIES = sorted([(code, code+" - "+babelfish.COUNTRIES[code]) for code in babelfish.COUNTRIES])
COUNTRIES.insert(0, ("US", "US - UNITED STATES"))
