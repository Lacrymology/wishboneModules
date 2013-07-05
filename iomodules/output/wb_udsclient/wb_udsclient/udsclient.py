#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  udsclient.py
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
from os import remove, path, makedirs, listdir
from itertools import cycle
import os
from gevent import Greenlet, sleep, socket
import stat
import logging


class UDSClient(Actor):
    '''**A Wishbone IO module which writes data into a Unix domain socket.**

    Writes data into a Unix domain socket.

    If more than one socket is provided, events are written in a
    round-robin way.

    Parameters:

        - name (str):       The instance name when initiated.
        - path (str):       The absolute path of the socket file or the socket pool.
        - delimiter (str):  When incoming data is a list, the data is joined and
                            submitted with the given delimiter.
        - limit (int):      The number of simultaneous greenthreads submitting events.
                            0 (or 1) for serial behavior.
        - stream (bool):    When True keeps the connection open.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events destined to the outside world.
    '''

    def __init__(self, name, limit=0, path=["/tmp/wishbone.socket"], delimiter="", stream=False ):
        Actor.__init__(self, name, limit=limit)
        self.name=name
        self.path=path
        self.delimiter=delimiter
        self.stream=stream

        if self.stream == False:
            self.next=cycle(path)
            self.sendSocket = self.__recreateSocket
        else:
            self.__setupSockets()
            self.sendSocket = self.__streamSocket
        self.logging.info('Initialiazed.')

    def consume(self, event):
        if isinstance(event['data'],list):
            self.sendSocket(self.delimiter.join(event['data']))
        else:
            self.sendSocket(event["data"])

    def __streamSocket(self, data):
        pass

    def __recreateSocket(self, data):
        while self.loop():
            try:
                location = self.next.next()
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.connect(location)
                sock.sendall(data)
                self.logging.debug('Data send.')
                sock.close()
                break
            except Exception as err:
                self.logging.warn('Connecting failed to %s. Will try again in a second. Reason: %s'%(location, err))
                sleep(1)

    def __setupSockets(self):
        pass

    def shutdown(self):
        self.logging.info('Shutdown')
