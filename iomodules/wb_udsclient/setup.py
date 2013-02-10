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

PROJECT = 'wb_udsclient'

VERSION = '0.1'


from setuptools import setup, find_packages

from distutils.util import convert_path
from fnmatch import fnmatchcase
import os
import sys

try:
    long_description = open('README.md', 'rt').read()
except IOError:
    long_description = ''

setup(
    name='wb_udsclient',
    version="0.1",
    description="A Wishbone IO module which writes data into a Unix domain socket.",
    author="Jelle Smet",
    packages=find_packages(),
    include_package_data=True,
    entry_points="""
        [wishbone.iomodule]
        UDSClient=wb_udsclient.udsclient:UDSClient
    """
)
