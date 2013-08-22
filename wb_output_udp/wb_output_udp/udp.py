#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  udp .py
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
from wishbone.tools import Measure
from gevent import socket, sleep, spawn
from gevent.event import Event

class UDP(Actor):
    '''**A Wishbone IO module to submit data over UDP.**

    Write data to a UDP socket.

    Parameters:

        - name (str):       The instance name when initiated.

        - host (string):    The host to submit to.
                            Default: "localhost"

        - port (int):       The port to submit to.
                            Default: 19283

    Queues:

        - inbox:    Incoming events submitted to the outside.
    '''

    def __init__(self, name, host="localhost", port=19283):
        Actor.__init__(self, name, setupbasic=False)
        self.createQueue("inbox", 1000)
        self.registerConsumer(self.consume, self.queuepool.inbox)

        self.name=name
        self.host=host
        self.port=port
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def consume(self, event):
        if isinstance(event["data"],list):
            data = ''.join(event["data"])
        else:
            data = event["data"]
        try:
            self.socket.sendto(str(data), (self.host, self.port))
        except Exception as err:
            self.logging.warn('Failed to submit data to %s port %s.  Reason %s.  Date purged..'%(self.host, self.port, err))

    def getSocket(self):
        '''Returns a socket object and locks inbox queue when this is not possible.
        '''

        while self.loop():
            try:

                return s
            except Exception as err:
                self.logging.warn("Failed to connect to %s port %s. Reason: %s. Retry in 1 second."%(self.host, self.port, err))
                sleep(1)