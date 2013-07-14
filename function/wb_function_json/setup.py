#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import setuptools
import re

###############################################################
from wb_function_json import JSON as docstring
PROJECT = 'wb_input_jsonconversion'
MODULE = 'JSON'
AUTHOR = "Jelle Smet"
URL = "https://github.com/smetj/wishboneModules"
INSTALL_REQUIRES= [ "jsonschema" ]
ENTRY_POINTS={
    "wishbone.function": [
        "jsonconversion = wb_function.jsonconversion.jsonconversion:JSONConversion"
    ]
}
###############################################################

VERSION = docstring.__version__

try:
    with open ("README.md", "w") as readme:
        readme.write(PROJECT+"\n")
        readme.write("="*len(PROJECT)+"\n\n")
        readme.write("version: %s\n\n"%(VERSION))
        readme.write(docstring.__doc__+"\n")
except:
    pass

try:
    with open('README.md') as readme:
        long_description = readme.read()
except:
    long_description=''

setuptools.setup(
    name=PROJECT,
    version=VERSION,
    description=re.search(".*?\*\*(.*?)\*\*",docstring.__doc__).group(1),
    long_description=long_description,
    author=AUTHOR,
    url=URL,
    install_requires=[ "wishbone" ] + INSTALL_REQUIRES,
    packages=setuptools.find_packages(),
    zip_safe=True,
    entry_points=ENTRY_POINTS
)
