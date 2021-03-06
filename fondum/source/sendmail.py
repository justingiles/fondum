import sendgrid
import sendgrid.helpers.mail as h
import python_http_client as sg_except
import parsing
import msg
from flask import current_app



###############################################
#
#  EMAIL SERVICE ROUTINES
#
#  CURRENTLY FOCUSED ON SENDGRID EMAIL SERVICE
#
###############################################

    # HAS_SENDMAIL = False
    # SENDGRID_NGROUP_LIST = []
    # SENDGRID_DEFAULT_FROM_ADDRESS = None
    # SENDGRID_DEFAULT_SUBJECT = None
    # SENDGRID_API_KEY = "to-be-determined"

def sendmail(group_id, to_addr=None, plain_text=None, creole_text=None, html=None, subject=None, from_addr=None):
    config = current_app.config
    #
    # do sanity checks first
    #
    if not config.get('HAS_SENDMAIL', False):
        return msg.bug("Sendmail not active in config.")
    if group_id not in config.get("SENDGRID_UNSUBSCRIBE_GROUPS", {}):
        return msg.bug("Sendgrid unsubscribe group_id {} not found.".format(group_id))
    from_header = from_addr or config.get("SENDGRID_DEFAULT_FROM_ADDRESS", None)
    if not from_header:
        return msg.bug("missing 'from' address.")
    to_header = to_addr
    if not to_header:
        return msg.bug("missing 'to' address.")
    subject_header = subject or config.get("SENDGRID_DEFAULT_SUBJECT", None)
    if not from_header:
        return msg.bug("missing subject.")
    if plain_text:
        body = plain_text
        mimetype = "text/plain"
    if creole_text:
        body = parsing.creole2html(creole_text)
        mimetype = "text/html"
    if html:
        body = html
        mimetype = "text/html"
    if not body:
        return msg.bug("missing body contents (via 'creole_text' or 'html' parameters.")
    #
    # 
    #
    # email_id = uuid.uuid4()
    # message.set_headers({'X-Fondum-EmailID': str(email_id)});
    try:
        sg = sendgrid.SendGridAPIClient(apikey=config['SENDGRID_API_KEY'])
        message = h.Mail(
            h.Email(from_header),
            subject_header,
            h.Email(to_header),
            h.Content(mimetype, body)
        )
        message.asm = h.ASM(group_id)
        response = sg.client.mail.send.post(request_body=message.get())
    except sg_except.UnauthorizedError as e:
        return msg.bug("SENDGRID unauthorized error (check SENDGRID_API_KEY): {}".format(str(e)))
    except Exception as e:
        return msg.bug("SENDGRID general error: {}".format(str(e)))
    return msg.success("Message sent to {}".format(to_header))
