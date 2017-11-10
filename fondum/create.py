import argparse
import os
from distutils import dir_util
import sys

import supercopy
from supercopy import SELF_NAME, NOW
from supercopy import tabbed_text, size_split, file_dict_swapper
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
    print ("CREATE project {}.".format(args.dir))
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
    # customizing the new directory using args.dir
    #
    if VERBOSE:
        print('n2. customizing based on command-line parameters')
    if args.docker:
        docker_target = args.docker
    else:
        docker_target = "default"
    file_dict_swapper("{}/settings/docker.json".format(root_dir), {'DOCKER_TARGET': docker_target})
    file_dict_swapper("{}/settings/general.json".format(root_dir), {'DOMAIN': args.dir})
    file_dict_swapper("{}/custom/main__pages.py".format(root_dir), {'DOMAIN': args.dir})
    file_dict_swapper("{}/settings/flask-settings.py".format(root_dir), {'DOMAIN': args.dir})
    #
    # generate web site
    #
    if VERBOSE:
        print('n3. runing compiler against the new web site.')
    comple.compile_project(args)

    if VERBOSE:
        print('n4. creating GIT repo.')
        print("...")
    os.chdir(root_dir)
    result = cmdline('git init')
    if VERBOSE:
        print(tabbed_text(result))
    os.chdir(orig_path)

    if VERBOSE:
        print('n5. done with creation of {}.'.format(args.dir))

# eof
