# -*- coding: utf-8 -*-
# !/usr/bin/python

import os
import time
import sys
import logging
from shutil import copytree

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S'
)

_help='''#######################################################################################################
Run command  : python odoo_flectra.py <path> [--copy/-c] [--help/-h]

@param -> odoo_flectra.py : to convert odoo modules to flectra
@param -> <path>         : give a path where your module is located
@param -> --copy OR -C   : this is an option parameter, pass if you want to make a copy before converting

@example> For Help       : python odoo_flectra.py [-h]
@example> Without Copy   : python odoo_flectra.py /home/<system_user>/<module_name>
@example> With Copy      : python odoo_flectra.py /home/<system_user>/<module_name> --copy

**Note ::
- If you execute this script on migrated module then there is possibility that you can get following kind of strings:
    -- "flectra, flectra",
    -- "odoo, flectra, flecta" 
- So do not use multiple times on migrated module.
- In case you get any error during execution, the best way, use --copy flag on your module,
so you can have a backup of your real data.

#######################################################################################################'''

if '--help' in sys.argv or '-H' in sys.argv or '-h' in sys.argv:
    print(_help)
    os._exit(1)

if len(sys.argv) < 2:
    logging.error('Directory path is required, pelase follow below instructions.')
    print(_help)
    os._exit(1)
else:
    odoo_path = sys.argv[1]
    if not os.path.isdir(odoo_path) and not os.path.exists(odoo_path):
        logging.error('Directory does not exist. Please check for path : %s' % odoo_path)
        print(_help)
        os._exit(1)

suffix = "/";
while odoo_path.endswith(suffix,len(odoo_path)-1) :
    odoo_path = odoo_path[:len(odoo_path)-1]

logging.info("You Directory is : %s" % odoo_path)
if '--copy' in sys.argv or '-C' in sys.argv or '-c' in sys.argv:
    logging.info('Please wait, copy is being process.')
    copytree(odoo_path, odoo_path+ time.strftime("%Y-%m-%d %H:%M:%S"))

replacements = {
    'odoo': 'flectra',
    'Odoo': 'Flectra',
    'ODOO': 'FLECTRA',
    '8069': '7073',
    'Part of Odoo.': 'Part of Odoo, Flectra.',
}

xml_replacements = {
    'odoo': 'flectra',
    'Odoo': 'Flectra',
    'ODOO': 'FLECTRA',
    'Part of Odoo.': 'Part of Odoo, Flectra.',
}

init_replacements = {
    'Odoo.': 'Odoo, Flectra.',
    'odoo': 'flectra',
}

manifest_replacements = {
    'Odoo.': 'Flectra.',
    'odoo': 'flectra',
}

re_replacements = {
    'Odoo.': 'Flectra.',
}

ingnore_dir = [
    'cla',
]

ingnore_files = [
    'LICENSE',
    'COPYRIGHT',
    'README.md',
    'CONTRIBUTING.md',
    'Makefile',
    'MANIFEST.in'
]

website_replacements = {
    'https://www.odoo.com': 'https://flectrahq.com',
    'www.odoo.com': 'https://flectrahq.com',
}

replace_email = {
    'info@odoo.com': 'info@flectrahq.com',
}

def init_files(root):
    infile = open(root + '__init__.py', 'rb').read()
    out = open(root + '__init__.py', 'wb')
    for i in init_replacements.keys():
        infile = infile.replace(i, init_replacements[i])
    out.write(infile)
    out.close

def manifest_files(root):
    temp = {}
    infile = open(root + '__manifest__.py', 'rb').read()
    temp.update(replace_email)
    temp.update(website_replacements)
    out = open(root + '__manifest__.py', 'wb')
    for i in temp.keys():
        infile = infile.replace(i, temp[i])
    out.write(infile)
    out.close()
    content_replacements(root, '__manifest__.py', manifest_replacements)

def xml_csv_json_files(root, name):
    infile = open(root + name, 'rb').read()
    out = open(root + name, 'wb')
    for i in replace_email.keys():
        infile = infile.replace(i, replace_email[i])
    for i in xml_replacements.keys():
        infile = infile.replace(i, xml_replacements[i])
    out.write(infile)
    out.close()

def python_files(root, name):
    infile = open(root + name, 'rb').read()
    out = open(root + name, 'wb')
    for i in replace_email.keys():
        infile = infile.replace(i, replace_email[i])
    out.write(infile)
    out.close()
    content_replacements(root, name, replacements)

def content_replacements(root, name, replace_dict):
    infile = open(root + name, 'rb').readlines()
    multilist = []
    if infile:
        for line in infile:
            words = line.split(' ')
            single_line = []
            for word in words:
                if word.startswith('info@') or word.startswith("'info@") or word.startswith('"info@'):
                    single_line.append(word)
                    continue
                for i in replace_dict.keys():
                    word = word.replace(i, replace_dict[i])
                single_line.append(word)
            multilist.append(single_line)
    with open('temp', 'ab') as temp_file:
        for lines in multilist:
            for word in lines:
                word = word if word.endswith('\n') else word + ' ' if word else ' '
                temp_file.write(word)
        os.rename('temp', root + name)

def rename_files(root, items):
    for name in items:
        logging.info(root + name)
        if name in ingnore_files:
            continue
        if name == '__init__.py':
            init_files(root)
        elif name == '__manifest__.py':
            manifest_files(root)
        else:
            sp_name = name.split('.')
            if len(sp_name) >= 2 and sp_name[-1] in ['xml', 'csv', 'json']:
                xml_csv_json_files(root, name)
            elif sp_name[-1] == 'py':
                python_files(root, name)
        try:
            for i in replacements.keys():
                if name != (name.replace(i, replacements[i])) :
                    logging.info('Rename With :: ' + name + ' -> ' + (name.replace(i, replacements[i])))
                    os.rename(root + name, root + (name.replace(i, replacements[i])))
        except OSError as e:
            pass

def rename_dir(root, items):
    for folder in items:
        if folder in ingnore_dir:
            continue
        for in_root, dirs, files in os.walk(root + folder, topdown=True):
            if files:
                rename_files(in_root + '/', files)
            if dirs:
                rename_dir(in_root + '/', dirs)
        if 'odoo' in folder:
            os.rename(root + folder, root + folder.replace('odoo','flectra'))

start_time = time.strftime("%Y-%m-%d %H:%M:%S")
if os.path.isdir(odoo_path):
    for root, dirs, files in os.walk(odoo_path, topdown=True):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        rename_files(root + '/', files)
        rename_dir(root + '/', dirs)
else:
    rename_files('',[odoo_path])
end_time = time.strftime("%Y-%m-%d %H:%M:%S")

logging.info('Execution Log :::: ')
logging.info('Start Time ::: %s' % start_time)
logging.info('End Time   ::: %s' % end_time)
