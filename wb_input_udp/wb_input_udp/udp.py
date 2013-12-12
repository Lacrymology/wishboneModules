#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  udp.py
#
#  Copyright 2013 Jelle Smet development@smetj.net
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

from wishbone import Actor
from gevent import spawn
from gevent.queue import Queue
from gevent.server import DatagramServer


class UDP(DatagramServer, Actor):
    '''**A Wishbone module which handles UDP input.**


    Parameters:

        - name(str):        The name you want this module to be registered under.

        - address(str):     The address to bind to.
                            Default: "0.0.0.0"

        - port(int):        The port on which the server should listen.
                            default: 19283

        - reuse_port(bool): Whether or not to set the SO_REUSEPORT socket option.
                            Allows multiple instances to bind to the same port.
                            Requires Linux kernel >= 3.9
                            Default: False



    Queues:

        - outbox:   Contains incoming events
    '''

    def __init__(self, name, address="0.0.0.0", port=19283):
        DatagramServer.__init__(self, "%s:%s"%(address, port))
        Actor.__init__(self, name, setupbasic=False)
        self.createQueue("outbox")
        self.name = name
        self._address = address
        self.port = port
        self.logging.info ( 'Started and listening on %s:%s' % (self._address, self.port) )

    def handle(self, data, address):
        '''Is called upon each incoming message, makes sure the data has the right Wishbone format and writes the it into self.inbox'''

        self.queuepool.outbox.put({'header':{},'data':data})

    def start(self):
        DatagramServer.start(self)

    def shutdown(self):
        '''This function is called on shutdown().'''
        self.logging.info('Shutdown')
