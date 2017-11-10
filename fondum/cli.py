#!/usr/bin/env python3
# coding: utf-8


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
import compose


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
    help="the web site domain name/directory"
)
parser_create.add_argument(
    "--docker",
    help="specificy docker target"
)

parser_compile = subparsers.add_parser(
    "compile",
    help="create website"
)
parser_compile.add_argument(
    "dir",
    type=str,
    help="the web site domain name/directory"
)
parser_compile.add_argument(
    "-p", "--passive",
    action="count",
    help="refrain from ever a deleting site directory in docker; simply overwrite"
)

parser_compose = subparsers.add_parser(
    "compose",
    help="compose docker with emphasis on website"
)
parser_compose.add_argument(
    "dir",
    type=str,
    help="the web site domain name/directory"
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
    elif args.cmd=="compose":
        compose.compose_dockers(args)
    elif args.cmd is None:
        print('ERROR: missing command-line argument. Use --help for help.')
    else:
        print('ERROR: "{}" command not valid.'.format(args.cmd))


if __name__ == "__main__":
    main()

