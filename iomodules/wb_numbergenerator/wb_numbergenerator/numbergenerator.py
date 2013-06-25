#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       numbergenerator.py
#
#       Copyright 2013 Jelle Smet development@smetj.net
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

import logging
from wishbone.toolkit import QueueFunctions, Block
from gevent import sleep, Greenlet
from gevent.queue import Queue

class NumberGenerator(Greenlet, QueueFunctions, Block):
    '''**A WishBone IO module which generates a continuing stream of increasing numbers. **


    Parameters:

        - name (str):       The instance name when initiated.

    Queues:

        - inbox:    Data generated
    '''

    def __init__(self, name):

        Greenlet.__init__(self)
        QueueFunctions.__init__(self)
        Block.__init__(self)
        self.logging = logging.getLogger( name )
        self.logging.info ( 'Initiated' )
        self.name = name


    def _run(self):
        self.logging.info('Started')
        x=0
        while self.block() == True:
            self.putData({"header":{},"data":x},'inbox')
            x+=1
            sleep()

    def shutdown(self):
        self.logging.info('Shutdown')
