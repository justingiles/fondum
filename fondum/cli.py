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

library_path = os.path.abspath(os.path.dirname(__file__))
if library_path not in sys.path:
    sys.path.insert(0, library_path)

import supercopy
from supercopy import SELF_NAME, NOW
from supercopy import tabbed_text
import create
import comple
import establish


parser = argparse.ArgumentParser(description="Fondum super-framework website management.")
parser.add_argument(
    "-v", "--verbose",
    action="count",
    help="increase output verbosity"
)
subparsers = parser.add_subparsers(help='sub-command help', dest='cmd')

parser_establish = subparsers.add_parser(
    "establish",
    help="establish root directory holding the website and docker sub-directories"
)

parser_create = subparsers.add_parser(
    "create",
    help="create website"
)
parser_create.add_argument(
    "dir",
    type=str,
    help="the web site domain name storing the web project"
)

parser_compile = subparsers.add_parser(
    "compile",
    help="create website"
)
parser_compile.add_argument(
    "dir",
    type=str,
    help="the web site domain name storing the web project"
)
parser_compile.add_argument(
    "-p", "--passive",
    action="count",
    help="refrain from ever a deleting site directory in docker; simply overwrite"
)


def main():
    # get the command line options
    #
    args = parser.parse_args()
    args.library_path = library_path
    if "dir" in args:
        if args.dir.endswith("/"):
            args.dir = args.dir[:-1]
    if args.cmd=="create":
        args.passive = False
        create.create_project(args)
    elif args.cmd=="compile":
        comple.compile_project(args)
    elif args.cmd=="establish":
        establish.establish_root(args)
    elif args.cmd is None:
        print('ERROR: missing command-line argument. Use --help for help.')
    else:
        print('ERROR: "{}" command not valid.'.format(args.cmd))


if __name__ == "__main__":
    main()

