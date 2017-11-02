from app import g
import copy
import msg

#
# Forms have something 'canned' in Flask using the WTForms library.
#
# However, reports do not. What is a query? Generically, it is a read-only
# view of database elements. A report of sorts. For the purpose of jcfs, it has
# very specific format, a header querey and a tabbet set of list queries.:
#
#   A "header" query shown at the top of the page. This query returns a single result.
#
#   A set of "list report" queries are shown after the header.
#   Each list query has it's own tab. Clicking on a tab brings up one list.
#
#   Both the header and list are optional. (Though, it is fairly pointless
#   to skip both.)
#
#   If there is only one list, it will still show the tab.
#
class Query(object):

    def __init__(self):
        self.status = msg.err("report not processed")

    def process(self, **kwargs):
        pass
