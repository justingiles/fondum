import os
import sys

from migration import post_dot_fondum, dot_fondum
from utility import cmdline


def establish_root(args):
    #
    # first, make sure we this is not already a fondum root directory
    #
    orig_path = os.getcwd()
    filename = "{}/.fondum".format(orig_path)
    if os.path.exists(filename):
        print("File '.fondum' already exists.")
        result = dot_fondum(orig_path, "root")
        if result["result"] is True:
            print("Stopping: this is already a fondum directory at version {}.".format(result['version']))
        else:
            print("Error: {}".format(result["result"]))
        exit()
    #
    print("ESTABLISH fondum root directory at {}.".format(orig_path))
    #
    # check OS environment
    #
    print("  01 looking for python 3.5 or better.")
    ver = sys.version_info
    if ver[0]==3 and ver[1]>=5:
        print("    > python {}.{} found.".format(ver[0], ver[1]))
    else:
        print("    > ERROR: python {}.{} found.".format(ver[0], ver[1]))
        exit()
    print("  02 looking for GIT.")
    result = cmdline('git --version')
    if result[0] and " version " in result[0]:
        print("    > git found.")
    else:
        print("    > ERROR! - don't see 'git'")
        exit()
    print('  03 looking for docker and docker-compose.')
    result = cmdline('docker --version')
    if result[0] and " version " in result[0]:
        print("    > docker found.")
    else:
        print("    > ERROR! - don't see docker")
        exit()
    result = cmdline('docker-compose --version')
    if result[0] and "docker-compose version" in result[0]:
        print("    > docker-compose found.")
    else:
        print("    > ERROR! - don't see docker-compose")
        exit()

    #
    # start
    #
    post_dot_fondum(orig_path, {"role": "root"})
    print("Done.")

# eof
