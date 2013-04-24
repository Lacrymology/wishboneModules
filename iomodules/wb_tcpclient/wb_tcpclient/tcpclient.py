#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tcpclient.py
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

from wishbone.toolkit import PrimitiveActor
from gevent import socket,sleep
from random import randint
import logging


class TCPClient(PrimitiveActor):
    '''**A Wishbone IO module which writes data to a TCP socket.**

    Writes data to a tcp socket.

    Pool should be a list of strings with format address:port.
    When pool has multiple entries, a random destination will be chosen.

    Parameters:

        - name (str):   The instance name when initiated.
        - pool (list):  A list of addresses:port entries.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events destined to the outside world.
    '''

    def __init__(self, name, pool=[]):
        PrimitiveActor.__init__(self, name)

        self.name=name
        self.pool=self.__splitAddress(pool)
        self.logging = logging.getLogger( name )
        self.logging.info('Initialiazed.')

    def __splitAddress(self, pool):
        p=[]
        for item in pool:
            address, port = item.split(":")
            p.append((address,int(port)))
        return p

    def consume(self, doc):

        if isinstance(doc["data"],list):
            data = ''.join(doc["data"])
        else:
            data = doc["data"]

        while self.block()==True:
            try:
                destination = self.pool[randint(0,len(self.pool)-1)]
                s=socket.socket()
                self.logging.debug("Writing data to %s"%(str(destination)))
                s.connect(destination)
                s.send(data)
                s.close()
                break
            except Exception as err:
                self.logging.warn("Failed to write data to %s. Reason: %s"%(str(destination), err))
                sleep(1)

    def shutdown(self):
        self.logging.info('Shutdown')
