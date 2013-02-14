#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  logging.py
#  
#  Copyright 2013 Jelle Smet <development@smetj.net>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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

import logging
from wishbone.toolkit import Block
from gevent import sleep


class Logging():
    def __init__(self, callback, interval=10):
        self.logging = logging.getLogger( 'Metrics module Logger' )
        self.logging.info("Initiated")
    
    def run(self):
        while self.block() == True:
            sleep(10)
