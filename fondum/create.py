import argparse
import os
import subprocess
from distutils import dir_util
import sys

import supercopy
from supercopy import SELF_NAME, NOW
from supercopy import tabbed_text

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

def size_split(s, n):
    def _f(s, n):
        while s:
            yield s[:n]
            s = s[n:]
    return list(_f(s, n))


def create_project(args):

    print ("Creating project {}.".format(args.dir))
    script_path = args.library_path
    root_dir = args.dir
    VERBOSE = args.verbose
    starter_dir = "{}/starter".format(script_path)
    orig_path = os.getcwd()
    #
    # create the subdirecories
    #
    if VERBOSE:
        print("1. Creating target directories.")
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
        print('2. runing compile.py against the new web site.')
    # result = cmdline('python3 {}/compile.py {} --verbose'.format(script_path, root_dir))
    # if VERBOSE:
    #     print(tabbed_text(result))
    comple.compile_project(args)

    # #
    # # create venv
    # #
    # if VERBOSE:
    #     print('3. creating virtualenv under "venv".')
    #     print("...")
    # os.chdir(root_dir)
    # result = cmdline('virtualenv venv')
    # if VERBOSE:
    #     print(tabbed_text(result))
    #     print("...")
    # result = cmdline('./update_requirements.sh')
    # if VERBOSE:
    #     print(tabbed_text(result))
    # os.chdir(orig_path)

    if VERBOSE:
        print('4. creating GIT repo.')
        print("...")
    os.chdir(root_dir)
    result = cmdline('git init')
    if VERBOSE:
        print(tabbed_text(result))
    os.chdir(orig_path)

    if VERBOSE:
        print('5. checking for docker and docker-compose.')
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
