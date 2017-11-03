import subprocess
import pathlib
import os

from __init__ import __version__


def parse_v0_1_1(source_lines, detail):
    detail["role"] = source_lines[1]
    return


# VERSION_MIGRATE = {
#     "0.1.2": future_migration_routine
# }

VERSION_PARSE = {
    "0.1.1": parse_v0_1_1
}

VERSIONS = [
    "0.1.1",
]


def dot_fondum(directory, expected_role):
    #
    # open file
    #
    filename = "{}/.fondum".format(directory)
    detail = {"result": "undefined error"}
    if not os.path.exists(filename):
        print(">>> Cancelling. {} is not a fondum-managed directory. (missing .fondum file).".format(directory))
        exit()
    source_text = pathlib.Path(filename).read_text()
    source_lines = [ln for ln in source_text.split("\n") if not ln.startswith("#")]
    if not source_lines:
        detail["result"] = "File {} is empty.".format(filename)
        return detail
    #
    # parse based on version
    #
    version = source_lines[0]
    detail["version"] = version
    if version in VERSIONS:
        VERSION_PARSE[version](source_lines, detail)
    else:
        detail["result"] = "Unable to parse the version {} code in {}. Upgrade fondum?".format(version, filename)
        return detail
    #
    # migrate if needed
    #
    if not version==__version__:
        # upgrade
        print("")
        while True:
            response = input(">>> This directory ({}) is at version {}. Migrate to version {} (y/n) ?".format(directory, __version__, __version__))
            if response=="y":
                migrate(directory, version)
                post_dot_fondum(directory, detail)
                break
            elif response=="n":
                print(">>> Cancelling. Unable to work on older code.")
                exit()
    #
    # check role
    #
    if expected_role!=detail['role']:
        detail["result"] = "{} is not a {} directory. It is a {} directory.".format(directory, expected_role, detail['role'])
        return detail
    #
    # return results
    #
    detail['result'] = True
    return detail


def post_dot_fondum(directory, details):
    filename = "{}/.fondum".format(directory)
    with open(filename, "wt") as f:
        f.write(__version__)
        f.write("\n")
        f.write(details["role"])
        f.write("\n")
    return


def migrate(directory, current_ver):
    # do nothing for now
    return


# eof
