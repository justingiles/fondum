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


# MSG_FOREGROUND = {
#     DEFAULT: "White",
#     SUCCESS: "White",
#     INFO: "White",
#     WARNING: "White",
#     DANGER: "White"
# }
# MSG_BACKGROUND = {
#     DEFAULT: "#337ab7",    
#     SUCCESS: "#5cb85c",
#     INFO: "#5bc0de",
#     WARNING: "#f0ad4e",
#     DANGER: "#d9534f"
# }

#
# LOGGING LEVELS
#
LOG_DEBUG = 0             # See Python "logging" for general interpretation
LOG_INFO = 1              # as a general rule, these levels match up with the PRESENTATION display_levels below
LOG_WARNING = 2
LOG_ERROR = 3
LOG_CRITICAL = 4

LOG_LEVEL_MAP = [10, 20, 30, 40, 50]
LOG_DESCRIPTION = {
    LOG_DEBUG: "DEBUG",
    LOG_INFO: "LOG_WARNING",
    LOG_WARNING: "WARNING",
    LOG_ERROR: "ERROR",
    LOG_CRITICAL: "CRITICAL"
}

#
# PRESENTATION
#

DISP_LOG = 0              # send to logs, if logs are stored, but not to end-user
DISP_SHOW = 1             # show to end-user; this is the default level; progress continues
DISP_WARNING = 2          # show to end-user; same as "display" but slightly more aggressive; but progress still continues
DISP_ERROR = 3            # this is an error that should be shown to user; a problem needs to be fixed
DISP_SECURITY_ALERT = 4   # security exception! this type of error should never normally happen

DISP_DESCRIPTION = {
    DISP_LOG: "LOG",
    DISP_SHOW: "SHOW",
    DISP_WARNING: "WARNING",
    DISP_ERROR: "ERROR",
    DISP_SECURITY_ALERT: "SECURITY_ALERT",
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
        self.log_level = LOG_LEVEL_MAP[LOG_INFO]
        self.return_def = None
        self.return_def_parms = {}
        self.flash_event = True

    def logger_level(self):
        return LOG_LEVEL_MAP[self.log_level]

    def import_logger_level(self, python_logger_level):
        level = 0
        for n in range(5):
            if python_logger_level >= LOG_LEVEL_MAP[n]:
                level = n
        self.log_level = level
        return

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


def msg(msg, level=DISP_SHOW, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DEFAULT
    fe.display_level = level
    fe.log_level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def message(*args, **kwargs):
    return msg(*args, **kwargs)


def note(msg, level=DISP_LOG, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DEFAULT
    fe.display_level = level
    fe.log_level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def success(msg, level=DISP_SHOW, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = SUCCESS
    fe.display_level = level
    fe.log_level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def info(msg, level=DISP_SHOW, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = INFO
    fe.display_level = level
    fe.log_level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def warning(msg, level=DISP_SHOW, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = WARNING
    fe.display_level = level
    fe.log_level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


# something went wrong but it is a normal kind of wrong. A user typing in a wrong
# password or using incorrect data in a field would generate an err. That is,
# having an 'err' occur is fully expected. The user simply needs to know that the
# operation failed.
def err(msg, level=DISP_SHOW, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DANGER
    fe.display_level = level
    fe.log_level = level
    fe.return_def = return_def
    fe.return_def_parms = kwargs
    return fe


def error(*args, **kwargs):
    return err(*args, **kwargs)


#
# used to return events that shouldn't ever really happen. i.e. a software bug
def bug(msg, level=DISP_ERROR, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DANGER
    fe.display_level = level
    fe.log_level = level
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
def security(msg, level=DISP_SECURITY_ALERT, return_def=None, **kwargs):
    fe = FlashEvent()
    fe.message = msg
    fe.event_type = DANGER
    fe.display_level = level
    fe.log_level = level
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
        if flash_event.display_level in [DISP_ERROR, DISP_SECURITY_ALERT]:
            return False
        return True
    if (flash_event is None) and not noneOkay:
        return False
    return True


def is_bad(flash_event, noneOkay=False):
    return not is_good(flash_event, noneOkay=noneOkay)


def flash(message, t=None, loglevel=None):
    ''' use 'flash' when you want the msg displayed to user when level is greater than 'DISP_LOG'. '''
    if not is_flashEvent(message):
        message = msg(message)
        if t in MSG_CAT_MAP:
            message.event_type = MSG_CAT_MAP[t]
        if loglevel:
            message.import_logger_level(loglevel)
    if message.display_level != DISP_LOG:
        flask.flash(message.message, MSG_FLASK_CAT[message.event_type])
    message.log()
    return


COUNTRIES = sorted([(code, code+" - "+babelfish.COUNTRIES[code]) for code in babelfish.COUNTRIES])
COUNTRIES.insert(0, ("US", "US - UNITED STATES"))
