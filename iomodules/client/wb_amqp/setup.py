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
import inspect
from os import path
from sys import version_info

PROJECT = 'wb_broker'
VERSION = '0.3'

#The goal is to have a .pth file so it can be included when creating RPMs
module_path=path.dirname((path.dirname(inspect.getfile(setuptools))))
pth_dir="./%s-%s-py%s.egg"%(PROJECT,
    VERSION,
    '.'.join(str(i) for i in version_info[0:2]))
pth=open ("%s.pth"%(PROJECT),'w')
pth.write(pth_dir)
pth.close()

try:
    with open('README.md') as file:
        long_description = file.read()
except:
    long_description=''

setuptools.setup(
    name=PROJECT,
    version=VERSION,
    description="A Wishbone AMQP client module.",
    long_description=long_description,
    author="Jelle Smet",
    url="https://github.com/smetj/wishboneModules",
    install_requires=['wishbone','amqp'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points="""
        [wishbone.client]
        Broker=wb_amqp.amqp:AMQP
    """
)
