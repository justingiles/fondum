import argparse
import os
import subprocess
from distutils import dir_util
import sys

import supercopy
from supercopy import SELF_NAME, NOW
from supercopy import tabbed_text, size_split

import comple

subdirectories_to_build = [
    "settings",
    "custom",
]


def cmdline(command):
    process = subprocess.Popen(
        args=command,
        stdout=subprocess.PIPE,
        shell=True
    )
    raw_text = process.communicate()[0].decode("utf-8") 
    return raw_text.split("\n")


def create_project(args):

    print ("Creating project {}.".format(args.dir))
    root_dir = args.dir
    VERBOSE = args.verbose
    starter_dir = "{}/starter_web".format(args.library_path)
    orig_path = os.getcwd()
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
