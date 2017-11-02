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
class Report(object):

    table_order = []

    def __init__(self):
        self.status = msg.err("report not processed")
        self.display_table = None
        self.table_name = None
        self.default_table_name = None

    def process(self, table_name=None, **kwargs):
        self.tables = []
        for table_class in self.table_order:
            self.tables.append(table_class())
        if self.tables:
            self.default_table_name = self.tables[0].key_name
        else:
            self.status = msg.err("no tables in report")
            return
        if not table_name:
            table_name = self.default_table_name
        self.table_name = table_name
        self.status = msg.err("table name [{}] not found".format(table_name))
        for table in self.tables:
            if table.key_name==table_name:
                self.display_table = table
                self.status = table.process_report_table(**kwargs)

class ReportTable(object):

    key_name = "not defined"
    table_name = "Not Defined"

    def __init__(self):
        self.rows = []
        self.header = None

    def set_header(self, empty_row):
        self.header = empty_row

    def add_row(self, row):
        self.rows.append(row)


class ReportRow(object):
    def __init__(self, d=None):
        self.items = []
        for class_attrib in self.__class__.__dict__:
            x = copy.deepcopy(self.__class__.__dict__[class_attrib])
            if isinstance(x, ReportItem):
                x.set_key(class_attrib)
                self.items.append(x)
        self.items.sort(key=lambda item: item.sort_position)
        #
        # now set values if d is passed
        #
        if d:
            for item in self.items:
                if hasattr(d, item.key):
                    item.value = d[item.key]
                    print("saved", item.value)

                    # item.value = copy.copy(d[item.key])

class ReportItem(object):
    def __init__(self, sort_position, desc=None, url=None):
        self.sort_position = sort_position
        self.desc = desc
        self.url = url
        self.justify = "left" # "left", "center", "right", "decimal:n"
        self.key = None
        self.value = None

    def set_key(self, name):
        self.key = name
        if not self.desc:
            self.desc = name

    def __repr__(self):
        return "<ReportItem key={}>".format(self.key)

