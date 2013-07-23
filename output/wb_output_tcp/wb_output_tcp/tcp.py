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
from gevent import socket, sleep, spawn
from wishbone.tools import Measure

class TCP(Actor):
    '''**A Wishbone IO module which writes data to a TCP socket.**

    Writes data to a tcp socket.

    Pool should be a list of strings with format address:port.
    When pool has multiple entries, a random destination will be chosen.

    Parameters:

        - name (str):       The instance name when initiated.

        - host (string):    The host to submit to.
                            Default: "localhost"

        - port (int):       The port to submit to.
                            Default: 19283

        - stream (bool):    Keep the connection open.
                            Default: False

        - rescue (bool):    When True events which failed to submit
                            successfully are put into the recue queue.
                            Default: False

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events destined to the outside world.
        - rescue:   Contains events which failed to go out succesfully.


    '''

    def __init__(self, name, limit=0, host="localhost", port=19283, timeout=1, stream=False, rescue=False):
        Actor.__init__(self, name, limit=limit)
        self.createQueue("rescue")
        self.name=name
        self.host=host
        self.port=port
        self.timeout=timeout
        self.stream=stream
        self.rescue=rescue
        self.__retry_seconds=1

        if self.stream == True:
            self.socket = self.getSocket()
            self.submit=self.__streamSubmit
        else:
            self.submit=self.__connectSubmit

        if self.rescue == True:
            self.do = self.__rescue
        else:
            self.do = self.__repeat

    def consume(self, event):
        self.submit(event["data"])


    @Measure.runTime
    def __streamSubmit(self, data):
        ''''''
        while self.loop():
            try:
                self.socket.send(str(data))
                break
            except Exception as err:
                self.logging.warn('Failed to submit data to %s port %s.  Reason %s'%(self.host, self.port, err))
                self.socket = self.getSocket()

    def getSocket(self):
        '''
        '''

        while self.loop():
            try:
                s = socket.socket()
                s.settimeout(self.timeout)
                s.connect((self.host, self.port))
                self.queuepool.inbox.putUnlock()
                return s
            except Exception as err:
                self.queuepool.inbox.putLock()
                self.logging.warn("Connection to %s port %s broken. Reason: %s. Will retry in %s seconds."%(self.host, self.port, err, self.__retry_seconds))
                sleep(self.__retry_seconds)

    @Measure.runTime
    def __connectSubmit(self, data):
        while self.loop():
            try:
                s = self.getSocket()
                s.send(str(data))
                s.close()
                break
            except:
                self.logging.warn('Failed to submit data to %s port %s.  Reason %s.  Trying again.'%(self.host, self.port, err))
                sleep(1)



    def __rescue(self, event):

        '''Executes submit.  When submit fails, the inbox is locked and events
        are submitted to the recue queue so they can be dealt with.  The inbox
        is unlocked with an increasing interval of maximum 64 seconds.  The
        advantage of this approach is that the inbox will be empty after a
        while (but rescue queue will be filled).'''

        if isinstance(event["data"],list):
            data = ''.join(event["data"])
        else:
            data = event["data"]

        try:
            self.submit(data)
            self.__retry_seconds=1
        except Exception as err:
            self.logging.warn("Failed to submit data to %s:%s.  Submitting to rescue queue.  Reason: %s"%(self.host, self.port, err))
            self.queuepool.rescue.put(event)
            if self.queuepool.inbox.isLocked() == (False, False):
                self.info("Locking inbox queue.")
                self.queuepool.inbox.putlock()
                self.info("Unlocking inbox in %s seconds"%(self.__retry_seconds))
                spawn_later(self.__retry_seconds, self.__unlockInbox)
                if self.__retry_seconds < 64:
                    self.__retry_seconds*=2


    def __repeat(self, event):

        '''Executes submit.  Retries failed submit attempts untill successfull
        with an increasing interval of maximum 64 seconds. Inbox queue is
        never locked.'''

        if isinstance(event["data"],list):
            data = ''.join(event["data"])
        else:
            data = event["data"]

        while self.loop():
            try:
                self.submit(data)
                self.__retry_seconds=1
                break
            except Exception as err:
                self.logging.warn("Failed to submit data to %s:%s.  Will retry.  Reason: %s"%(self.host, self.port, err))
                #sleep(self.__retry_seconds)
                if self.__retry_seconds < 64:
                    self.__retry_seconds*=2


    def __unlockInbox(self):
        self.info("Unlocking inbox.")
        self.queuepool.inbox.putUnlock()

    def shutdown(self):
        self.logging.info('Shutdown')
