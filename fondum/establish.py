import os

from migration import post_dot_fondum, dot_fondum

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
    # start
    #
    print("Establishing fondum root directory at {}.".format(orig_path))
    post_dot_fondum(orig_path, {"role": "root"})
    print("Done.")

# eof
