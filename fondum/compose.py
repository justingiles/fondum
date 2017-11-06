import argparse
import os
import shutil
import sys
from distutils import dir_util
import json
from pathlib import Path
import re

import supercopy
from supercopy import SELF_NAME, NOW
from supercopy import tabbed_text, size_split
from utility import cmdline
from migration import post_dot_fondum, dot_fondum


def compose_dockers(args):
    print("Composing docker group(s) associated with {}.".format(args.dir))
    orig_path = os.getcwd()

    if args.verbose:
        VERBOSE = True
    else:
        VERBOSE = False

    #
    # gather root information
    #
    root_path = Path('./')
    r = [f for f in root_path.iterdir() if f.is_dir()]
    root_web_repo_directories = [d.name for d in r if not d.name.startswith("docker_")]
    root_docker_directories = [d.name for d in r if d.name.startswith("docker_")]
    #
    # gather website target source information
    #
    if VERBOSE:
        print("d01 gathering details about website.")    
    details = dot_fondum(args.dir, "site")
    if details["result"] is not True:
        print("ERROR: {}".format(details["result"]))
        exit()
    with open("{}/settings/docker.json".format(args.dir)) as f:
        docker_detail = json.load(f)
    target_docker = docker_detail["target"]
    target_dir = "docker_{}".format(target_docker)
    if VERBOSE:
        print('    > target docker is "{}" in directory ./{}'.format(target_docker, target_dir))
    #
    # gather docker directory information
    #
    if VERBOSE:
        print("d02 gathering details about docker.")    
    docker_path = Path('./{}'.format(target_dir))
    dp = [f for f in docker_path.iterdir() if f.is_dir()]
    docker_site_directories = [d.name for d in dp if d.name.startswith("fondum_")]
    docker_sites = [d[7:] for d in docker_site_directories]
    print(docker_sites)


    if VERBOSE:
        print("d03 building docker-compose.yml.")
    with open("{}/templates/docker-compose.yml".format(args.library_path)) as f:
        doc = f.read()
    with open("{}/templates/docker-compose.yml.site".format(args.library_path)) as f:
        site_template = f.read()
    ext_template = "            - fondum_{{site}}"
    site_import_text = ""
    ext_import_text = ""
    for site in docker_sites:
        site_text = site_template.replace("{{site}}", site)
        site_import_text += site_text
        site_import_text += "\n"
        ext_text = ext_template.replace("{{site}}", site)
        ext_import_text += ext_text
        ext_import_text += "\n"
    doc = doc.replace("# {{{--INSERT-MARKER-1--}}}", site_import_text, 1)
    doc = doc.replace("# {{{--INSERT-MARKER-2--}}}", ext_import_text, 1)
    manual_filename = "{}/docker-compose.yml.INCLUDE".format(target_dir)
    if not os.path.exists(manual_filename):
        with open(manual_filename, "w+") as f:
            f.write("# This file, if used, is inserted AS-IS into the end of docker-compose.yml.\n")
            f.write("# \n")
            f.write("# TODO: in the future, it will be possible to suppress docker-compose 'site'\n")
            f.write("#       generation of fondum sites with a value in the \n")
            f.write("#       <site>/settings/docker.json file.\n")
    with open(manual_filename) as f:
        manually_added_text = f.read()
    doc = doc.replace("# {{{--INSERT-MARKER-3--}}}", manually_added_text, 1)
    with open("{}/docker-compose.yml".format(target_dir), "w") as f:
        f.write(doc)


    nginx_site_dir = "{}/nginx/sites-enabled".format(target_dir)
    if VERBOSE:
        print("d04 updating NGINX sites (at {}).".format(nginx_site_dir))
    if os.path.exists(nginx_site_dir):
        for fn in os.listdir(nginx_site_dir):
            if fn.startswith("fondum_"):
                os.remove(os.path.join(nginx_site_dir, fn))
    else:
        supercopy.create_dir(nginx_site_dir)
    with open("{}/templates/nginx.site.template".format(args.library_path)) as f:
        nginx_template = f.read()
    for site in docker_sites:
        nginx_text = nginx_template.replace("{{site}}", site)
        with open("{}/fondum_{}".format(nginx_site_dir, site), "w+") as f:
            f.write(nginx_text)

    if VERBOSE:
        print("d05 building docker.")


    if VERBOSE:
        print("d06 checking for discrepancies in other dockers.")    


    if VERBOSE:
        print("d07 done with docker group composition.")

# eof
