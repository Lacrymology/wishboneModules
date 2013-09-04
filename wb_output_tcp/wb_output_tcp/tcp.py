#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tcp.py
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

class TCP(Actor):
    '''**A Wishbone IO module which writes data to a TCP socket.**

    Writes data to a tcp socket.

    Parameters:

        - name (str):       The instance name when initiated.

        - host (string):    The host to submit to.
                            Default: "localhost"

        - port (int):       The port to submit to.
                            Default: 19283

        - timeout(int):     The time in seconds to timeout when
                            connecting
                            Default: 1

        - delimiter(str):   A delimiter to add to each event.
                            Default: "\n"

    Queues:

        - inbox:    Incoming events submitted to the outside.

        - rescue:   Contains events which failed to go out succesfully.


    '''

    def __init__(self, name, host="localhost", port=19283, timeout=10, delimiter="\n"):
        Actor.__init__(self, name, setupbasic=False)
        self.createQueue("rescue")
        self.createQueue("inbox", 1000)
        self.queuepool.inbox.putLock()
        self.registerConsumer(self.consume, self.queuepool.inbox)

        self.name=name
        self.host=host
        self.port=port
        self.timeout=timeout
        self.delimiter=delimiter

        self.__connect=Event()
        self.__connect.set()

    def preHook(self):
        spawn(self.connectionMonitor)

    #@Measure.runTime
    def consume(self, event):
        if isinstance(event["data"],list):
            data = ''.join(event["data"])
        else:
            data = event["data"]
        try:
            self.socket.send(str(data)+self.delimiter)
        except Exception as err:
            self.__connect.set()
            self.logging.debug('Failed to submit data to %s port %s.  Reason %s. Sending back to rescue queue.'%(self.host, self.port, err))

    def connectionMonitor(self):
        while self.loop():
            self.__connect.wait()
            self.queuepool.inbox.putLock()
            try:
                self.socket.close()
            except:
                pass
            self.socket=self.getSocket()
            self.queuepool.inbox.putUnlock()
            self.__connect.clear()

    def getSocket(self):
        '''Returns a socket object and locks inbox queue when this is not possible.
        '''

        while self.loop():
            try:
                s = socket.socket()
                s.settimeout(self.timeout)
                s.connect((self.host, self.port))
                self.logging.info("Connected to %s port %s."%(self.host, self.port))
                return s
            except Exception as err:
                self.logging.warn("Failed to connect to %s port %s. Reason: %s. Retry in 1 second."%(self.host, self.port, err))
                sleep(1)