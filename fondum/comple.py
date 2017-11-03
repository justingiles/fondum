import argparse
import os
import shutil
import sys
from distutils import dir_util
import json
import pathlib
import re

import supercopy
from supercopy import SELF_NAME, NOW
from supercopy import tabbed_text, size_split
from utility import cmdline
from migration import post_dot_fondum, dot_fondum


def string_before(s, last):
    try:
        return s.partition(last)[0]
    except ValueError:
        return None


def string_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return None


def convert_camel_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


def url_smash(*arglists, force_kw=False):
    final_list = []
    for arglist in arglists:
        for arg in arglist:
            result = arg
            if force_kw:
                if "=" not in arg:
                    result = "{}={}".format(arg, arg)
            final_list.append(result)
    smash = "/".join(final_list)
    return "/{}/".format(smash)


def arg_smash(*arglists, force_kw=False):
    final_list = []
    for arglist in arglists:
        for arg in arglist:
            result = arg
            if force_kw:
                if "=" not in arg:
                    result = "{}={}".format(arg, arg)
            final_list.append(result)
    smash = ", ".join(final_list)
    return "{}".format(smash)


def compile_project(args):
    print("Compiling project {}.".format(args.dir))
    source_dir = "{}/source".format(args.library_path)
    starter_docker_dir = "{}/starter_docker".format(args.library_path)
    settings_dir = "{}/settings".format(args.dir)
    custom_dir = "{}/custom".format(args.dir)
    orig_path = os.getcwd()

    if args.verbose:
        VERBOSE = True
    else:
        VERBOSE = False

    details = dot_fondum(args.dir, "site")
    if details["result"] is not True:
        print("Error: {}".format(details['result']))
        exit()

    # reading/rendering settings files
    settings_files = os.listdir(settings_dir)
    if VERBOSE:
        print("c01 reading JSON settings files..")
    stg = {}
    for filename in settings_files:
        if filename.endswith(".json"):
            if VERBOSE:
                print("   > parsing {}".format(filename))
            base = os.path.basename(filename)
            category = os.path.splitext(base)[0]
            with open("{}/{}".format(settings_dir, filename)) as f:
                stg[category] = json.load(f)
                # print(stg)
    if "docker" not in stg:
        print("   ERROR: {}/docker.json file was missing!".format(settings_dir))
        ImportError("general settings file(s) missing")
    if "target" not in stg["docker"]:
        print("   ERROR: docker.json missing 'target'!".format(settings_dir))
        ImportError("json entry missing")
    docker_name = "docker_{}".format(stg["docker"]['target'])
    destination_dir = "{}/site_{}".format(docker_name, args.dir)

    #
    if VERBOSE:
        print("c02 prepping docker destination ({} for {})".format(docker_name, stg["docker"]['target']))
    if not os.path.exists(docker_name):
        if VERBOSE:
            print('    > creating the docker directory and git repo.')
        os.makedirs(docker_name)
        dir_util.copy_tree(starter_docker_dir, docker_name)
        post_dot_fondum(docker_name, {"role": "docker"})
        os.chdir(docker_name)
        result = cmdline('git init')
        if VERBOSE:
            print(tabbed_text(result))
        os.chdir(orig_path)

 
    # delete original site directory
    if args.passive:
        if VERBOSE:
            print("c02b running passive; so skipping fresh 'site' directory deletion")
    else:
        if VERBOSE:
            print("c02b deleting site subdirectory in docker if needed.")
        if os.path.exists(destination_dir):
            dir_util.remove_tree(destination_dir, verbose=VERBOSE)


    # move source files
    #
    source_files = os.listdir(source_dir)
    if VERBOSE:
        print("c03 moving fixed source files to correct location.")
    supercopy.copy_dir(source_dir, destination_dir, verbose=VERBOSE)

    # move key settings file(s)
    #
    if VERBOSE:
        print("c04 moving flask-settings.py file to correct location.")
    # shutil.copy("{}/flask-settings.py".format(settings_dir), destination_dir)
    supercopy.copy_file("flask-settings.py", settings_dir, destination_dir, verbose=VERBOSE)

    # move custom files
    #
    if VERBOSE:
        print("c05 moving custom files to correct location.")
    supercopy.copy_dir(custom_dir, destination_dir, verbose=VERBOSE)
    custom_files = [fn.rsplit(".", 1)[0] for fn in os.listdir(custom_dir) if fn.endswith(".py")]
    #
    # combined model
    #
    model_lines = [
        "import {}".format(fn) for fn in custom_files if fn.endswith("__models")
    ]
    model_import_text = "\n".join(model_lines)
    if VERBOSE:
        print("06A compiling models references.")
        print(tabbed_text(model_lines, 4))
    #
    # combined database
    #
    database_lines = [
        "import {}".format(fn) for fn in custom_files if fn.endswith("__database")
    ]
    database_import_text = "\n".join(database_lines)
    if VERBOSE:
        print("c06B compiling database references.")
        print(tabbed_text(database_lines, 4))
    #
    # pages
    #
    if VERBOSE:
        print("c06C compiling Page references.")
    page_files = [fn.rsplit(".", 1)[0] for fn in os.listdir(destination_dir) if fn.endswith("__pages.py")]
    page_lines = [
        "import {}".format(fn) for fn in page_files
    ]
    if VERBOSE:
        print(tabbed_text(page_lines, 4))
    page_views_text = "\n".join(page_lines)
    page_views_text += "\n\n"
    for filename in page_files:
        full_filename = "{}.py".format(filename)
        source_text = pathlib.Path("{}/{}".format(destination_dir, full_filename)).read_text()
        group_name = string_before(full_filename, "__pages.py")
        class_lines = [ln for ln in source_text.split("\n") if ln.startswith("class ")]
        for class_line in class_lines:
            class_name = string_between(class_line, "class ", "(Page")
            if class_name is None:
                continue
            class_name = class_name.strip()
            class_parts = class_name.split("__")
            page_name = convert_camel_case(class_parts[0])
            page_parms = []
            if len(class_parts) > 1:
                page_parms = class_parts[1:]
                parms_text = "\{{}}".format(",".join(["'{}': '{}'".format(p, p) for p in page_parms]))
            def_name = "page_{}_{}".format(group_name, page_name.replace("-", "_"))
            key = "{}/{}".format(group_name, page_name)
            bracket_parms = ["<{}>".format(parm) for parm in page_parms]
            url = url_smash([group_name, page_name], bracket_parms)
            t = page_parms + ["TABLE_NAME=None"]
            def_parameters = ", ".join(parm for parm in t)
            t = page_parms + ["TABLE_NAME"]
            just_parameters = ", ".join(parm for parm in t)
            # PLAIN
            page_views_text += "@app.route('{}', methods=['GET', 'POST'])\n".format(url)
            page_views_text += "def {}({}):\n".format(def_name, def_parameters)
            page_views_text += "    page = {}.{}()\n".format(filename, class_name)
            page_views_text += "    page.process({})\n".format(arg_smash(page_parms, ["TABLE_NAME"], force_kw=True))
            page_views_text += "    if page.MainForm:\n"
            page_views_text += "        page.wtf = page.MainForm()\n"
            if page_parms:
                page_views_text += "    return page_handler(\n"
                page_views_text += "        page,\n"
                page_views_text += "        '{}',\n".format(def_name)
                page_views_text += "        '{}',\n".format(key)
                m = "\n".join(["        {}={}".format(p, p) for p in page_parms])
                page_views_text += "{}\n".format(m)
                page_views_text += "    )\n"
            else:
                page_views_text += "    return page_handler(page, '{}', '{}')\n".format(def_name, key)
            page_views_text += "\n\n"
            # FOR TABLES
            page_views_text += "@app.route('{}<TABLE_NAME>/', methods=['GET', 'POST'])\n".format(url)
            page_views_text += "def {}__TABLE_NAME({}):\n".format(def_name, just_parameters)
            page_views_text += "    return {}({})\n".format(def_name, arg_smash(page_parms, ["TABLE_NAME=TABLE_NAME"]))
            page_views_text += "\n\n"
            #
            if VERBOSE:
                print("    > parsed route {}".format(url))
    #
    # index
    #
    if VERBOSE:
        print("c06D compiling index.")
    index_def = stg["general"]["index_def"]
    index_view_text = ""
    index_view_text += "@app.route('/', methods=['GET'])\n"
    index_view_text += "def index():\n"
    index_view_text += '    return {}()\n'.format(index_def)
    index_view_text += "\n\n"


    #
    # combined views
    #
    if VERBOSE:
        print("c07 compiling combined views.py file.")

    views_lines = [
        "from {} import *".format(fn) for fn in custom_files if fn.endswith("__views")
    ]
    import_text = "\n".join(views_lines)
    if VERBOSE:
        print(tabbed_text(views_lines, 4))
    import_text += "\n\n\n"
    import_text += page_views_text
    if VERBOSE:
        print("    > added parsed routes from queries")
    import_text += "\n\n"
    import_text += index_view_text
    if VERBOSE:
        print("    > added index route")
    source = "{}/{}".format(destination_dir, "views.py")
    source_text = pathlib.Path(source).read_text()
    final_text = source_text.replace("# {{{--INSERT-MARKER--}}}", import_text, 1)
    with open("{}/{}".format(destination_dir, "views.py"), 'wt') as f:
        f.write(final_text)

    #
    # compiling key files
    #
    settings_files = os.listdir(settings_dir)
    if VERBOSE:
        print("c08 compiling key files..")
    if "general" in stg:
        with open("{}/jcfs_settings.py".format(destination_dir), "w") as pfile:
            if VERBOSE:
                print('   > writing "jcfs_settings.py" file')
                pfile.write("# DO NOT EDIT. This file was autogenerated by the jcfs compile function.\n")
            pfile.write(supercopy.pretty_dictionary(stg[category], "s"))
            pfile.write("\n")
            pfile.write("# eof\n")
    else:
        print("   ERROR: {}/general.json file was missing!".format(settings_dir))
        ImportError("general settings file(s) missing")


    if VERBOSE:
        print("c09 done with compile.")

# eof
