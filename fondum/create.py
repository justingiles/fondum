import argparse
import os
from distutils import dir_util
import sys

import supercopy
from supercopy import SELF_NAME, NOW
from supercopy import tabbed_text, size_split
from utility import cmdline
from migration import post_dot_fondum, dot_fondum

import comple

subdirectories_to_build = [
    "settings",
    "custom",
]


def create_project(args):
    #
    # first, make sure we are running from a legit root directory
    #
    orig_path = os.getcwd()
    result = dot_fondum(orig_path, "root")
    #
    # start
    #
    print ("Creating project {}.".format(args.dir))
    root_dir = args.dir
    VERBOSE = args.verbose
    starter_dir = "{}/starter_web".format(args.library_path)
    #
    # check common domain name flaws
    #
    if "." not in args.dir:
        print('ERROR: "{}" does not appear to be a domain name.'.format(args.dir))
    if args.dir.endswith(".") or args.dir.startswith("."):
        print('ERROR: "{}" does not appear to be a domain name.'.format(args.dir))
    if ("/" in args.dir) or ("\\" in args.dir):
        print('ERROR: "{}" does not appear to be a domain name.'.format(args.dir))
    #
    # create the subdirecories
    #
    if VERBOSE:
        print("n1. Creating target directories.")
    if not os.path.exists(root_dir):
        if VERBOSE:
            print('    > creating the "{}" directory.'.format(root_dir))
        os.makedirs(root_dir)
        dir_util.copy_tree(starter_dir, root_dir)
        post_dot_fondum(root_dir, {"role": "site"})
    else:
        print('    > FAIL: the "{}" directory already exists.'.format(args.dir))
        exit()
    #
    # generate web site
    #
    if VERBOSE:
        print('n2. runing compiler against the new web site.')
    comple.compile_project(args)

    if VERBOSE:
        print('n3. creating GIT repo.')
        print("...")
    os.chdir(root_dir)
    result = cmdline('git init')
    if VERBOSE:
        print(tabbed_text(result))
    os.chdir(orig_path)
    #
    # check OS environment
    #
    if VERBOSE:
        print('n4. checking for docker and docker-compose in OS.')
    result = cmdline('docker --version')
    if result[0] and " version " in result[0]:
        if VERBOSE:
            print("    > docker found.")
    else:
        print("    > ERROR! - don't see docker")
        exit()
    result = cmdline('docker-compose --version')
    if result[0] and "docker-compose version" in result[0]:
        if VERBOSE:
            print("    > docker-compose found.")
    else:
        print("    > ERROR! - don't see docker-compose")
        exit()

    if VERBOSE:
        print('n5. done with creation of {}.'.format(args.dir))

# eof
