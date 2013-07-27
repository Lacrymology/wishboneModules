#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  uds.py
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

class UDS(Actor):
    '''**A Wishbone IO module which writes data to a Unix domain socket.**

    Writes data to a unix domain socket.


    Parameters:

        - name (str):       The instance name when initiated.

        - path (string):    The path to the domain socket.
                            Default: "/tmp/wishbone"

        - stream (bool):    Keep the connection open.
                            Default: False

        - rescue (bool):    When True events which failed to submit
                            successfully are put into the recue queue.
                            Default: False

    Queues:

        - inbox:    Incoming events submitted to the outside.
        - rescue:   Contains events which failed to go out succesfully.


    '''

    def __init__(self, name, limit=0, path="/tmp/wishbone", stream=False, rescue=False):
        Actor.__init__(self, name, limit=limit, setupbasic=False)
        self.createQueue("rescue")
        self.createQueue("inbox", 1000)
        self.queuepool.inbox.putLock()
        self.registerConsumer(self.consume, self.queuepool.inbox)
        self.name=name
        self.path=path
        self.stream=stream
        self.rescue=rescue
        self.__retry_seconds=1
        self.__create_socket_busy=Event()
        self.__create_socket_busy.clear()

        if self.stream == True:
            self.submit=self.__streamSubmit
        else:
            self.submit=self.__connectSubmit

        spawn(self.testConnection)

    def consume(self, event):

        self.submit(event)

    @Measure.runTime
    def __streamSubmit(self, event):

        '''Submits each event to an already opened socket <self.socket>.
        '''

        if isinstance(event["data"],list):
            data = ''.join(event["data"])
        else:
            data = event["data"]

        while self.loop():
            try:
                self.socket.send(str(data))
                break

            except Exception as err:
                if self.rescue == True:
                    self.logging.debug('Failed to submit data to %s.  Reason %s. Sending back to rescue queue.'%(self.path, err))
                    self.queuepool.rescue.put(event)
                    spawn(self.createStreamSocket)
                    break
                else:
                    self.logging.debug('Failed to submit data to %s.  Reason %s'%(self.path, err))
                    self.socket=self.getSocket()
                    self.logging.info("Connected to %s."%(self.path))

    @Measure.runTime
    def __connectSubmit(self, event):

        '''For each events, opens a socket writes data to it and closes it.
        '''

        if isinstance(event["data"],list):
            data = ''.join(event["data"])
        else:
            data = event["data"]

        while self.loop():
            try:
                s = self.getSocket()
                s.send(str(data))
                s.close()
                break
            except Exception as err:
                if self.rescue == True:
                    self.logging.warn('Failed to submit data to %s.  Reason %s. Sending back to rescue queue.'%(self.path, err))
                    self.queuepool.rescue.put(event)
                    break
                else:
                    self.logging.warn('Failed to submit data to %s.  Reason %s.  Trying again in %s seconds.'%(self.path, err, self.__retry_seconds))
                    sleep(1)

    def createStreamSocket(self):
        '''Creates <self.socket>.
        Locking prevents multiple instances running at the same time.
        '''
        if not self.__create_socket_busy.isSet():
            self.__create_socket_busy.set()
            self.socket = self.getSocket()
            self.logging.info("Connected to %s."%(self.path))
            self.__create_socket_busy.clear()

    def getSocket(self):
        '''Returns a socket object and locks inbox queue when this is not possible.
        '''

        retrying = False

        while self.loop():
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.connect(self.path)
                if retrying == True:
                    self.queuepool.inbox.putUnlock()
                    self.logging.debug("Unlocked inbox for incoming data.")
                return s
            except Exception as err:
                retrying = True
                if self.queuepool.inbox.isLocked()[1] == False:
                    self.queuepool.inbox.putLock()
                    self.logging.debug("Locking inbox for incoming data.")
                self.logging.warn("Failed to connect to %s. Reason: %s. Will retry in %s seconds."%(self.path, err, self.__retry_seconds))
                sleep(self.__retry_seconds)

    def testConnection(self):
        '''Tries to connect to the destination and unlocks <inbox> queue when
        this succeeds.'''

        if self.stream == True:
            self.socket = self.getSocket()
        else:
            self.getSocket().close()

        self.queuepool.inbox.putUnlock()
