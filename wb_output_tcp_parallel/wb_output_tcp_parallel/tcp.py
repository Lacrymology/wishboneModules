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
import thread

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
                            Default: "\\n"

        - success (bool):   When True, submits succesfully outgoing
                            events to the 'success' queue.
                            Default: False

        - failed (bool):    When True, submits failed outgoing
                            events to the 'failed' queue.
                            Default: False

        - block(bool):      When False, it doesn't stop events from
                            entering the inbox queue.
                            Default: True

    Queues:

        - inbox:    Incoming events submitted to the outside.

        - success:  Contains events which went out succesfully.
                    (optional)

        - failed:   Contains events which did not go out successfully.
                    (optional)


    '''

    def __init__(self, name, host="localhost", port=19283, timeout=10,
                 delimiter="\n", success=False, failed=False):
        Actor.__init__(self, name, setupbasic=False)
        self.createQueue("inbox")

        self.registerConsumer(self.consume, self.queuepool.inbox)

        self.name=name
        self.host=host
        self.port=port
        self.timeout=timeout
        self.delimiter=delimiter

    def sendEvent(self, event):
        """
        Short-lived Greenlet that sends one event through a newly created tcp
        socket and then discards it
        """
        data = event["data"]
        if isinstance(data, list):
            data = self.delimiter.join(data)

        while self.loop():
            try:
                s = self.getSocket()
                s.sendall(str(data) + self.delimiter)
                self.logging.info("Data sent")
                thread.exit()
            except Exception, e:
                self.logging.warn("Problem sending data: %s" % e)

    def consume(self, event):
        thread.start_new_thread(self.sendEvent, (event,))

    def getSocket(self):
        '''
        Returns a socket object
        '''

        while self.loop():
            try:
                s = socket.socket()
                s.settimeout(self.timeout)
                s.connect((self.host, self.port))
                self.logging.info("Connected to %s port %s."%(self.host, self.port))
                return s
            except Exception as err:
                self.logging.warn("Failed to connect to %s port %s. Reason: "
                                  "%s. Retry in 10 milliseconds." % (self.host,
                                                                    self.port,
                                                                    err))
                sleep(1)
