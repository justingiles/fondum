#!/usr/bin/env python3
# coding: utf-8

"""
Fondum
Usage:
  fondum create <domain-name>
  fondum compile <domain-name>
  fondum -v | --version
  fondum -h | --help
Options:
  -h, --help          Help information.
  -v, --version       Show version.
"""

import argparse
import os
import subprocess
from distutils import dir_util
import sys

# Insert project root path to sys.path
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

import supercopy
from supercopy import SELF_NAME, NOW
from supercopy import tabbed_text
import create
import comple

parser = argparse.ArgumentParser(description="Create the initial web site into a new directory.")
parser.add_argument(
    "cmd",
    type=str,
    help="command to run"
)
parser.add_argument(
    "dir",
    type=str,
    help="the web site domain name storing the web project"
)
parser.add_argument(
    "-v", "--verbose",
    action="count",
    help="increase output verbosity"
)
parser.add_argument(
    "-p", "--passive",
    action="count",
    help="refrain from ever a deleting directory; simply overwrite"
)


def main():
    # get the command line options
    #
    args = parser.parse_args()
    args.script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    # print("GOT IT", args.cmd, args.dir, "script=", args.script_path)
    if args.cmd=="create":
        create.create_project(args)
    elif args.cmd=="compile":
        comple.compile_project(args)
    else:
        print('ERROR: "{}" command not valid.'.format(args.cmd))


if __name__ == "__main__":
    main()

