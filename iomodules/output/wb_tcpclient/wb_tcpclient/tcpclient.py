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

from wishbone import Actor
from gevent import socket,sleep
from random import randint
from wishbone.tools import Measure

class TCPClient(Actor):
    '''**A Wishbone IO module which writes data to a TCP socket.**

    Writes data to a tcp socket.

    Pool should be a list of strings with format address:port.
    When pool has multiple entries, a random destination will be chosen.

    Parameters:

        - name (str):       The instance name when initiated.
        - pool (list):      A list of addresses:port entries.
        - stream (bool):    Keep the connection open.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events destined to the outside world.
    '''

    def __init__(self, name, pool=[]):
        Actor.__init__(self, name, limit=0)
        self.name=name
        self.pool=self.__splitAddress(pool)

    def __splitAddress(self, pool):
        p=[]
        for item in pool:
            address, port = item.split(":")
            p.append((address,int(port)))
        return p

    @Measure.runTime
    def consume(self, event):

        if isinstance(event["data"],list):
            data = ''.join(event["data"])
        else:
            data = event["data"]

        while self.loop()==True:
            #try:
                destination = self.pool[randint(0,len(self.pool)-1)]
                s=socket.socket()
                s.settimeout(1)
                s.connect(destination)
                self.logging.debug("Writing data to %s"%(str(destination)))
                s.sendall(data)
                s.close()
                break
            # except Exception as err:
            #     self.logging.warning("Failed to write data to %s. Reason: %s"%(str(destination), err))
            #     sleep(1)

    def shutdown(self):
        self.logging.info('Shutdown')
