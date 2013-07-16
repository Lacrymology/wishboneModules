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

    def __init__(self, name, host="localhost", port=19283, stream=False, rescue=False):
        Actor.__init__(self, name, limit=0)
        self.createQueue("rescue")
        self.name=name
        self.host=host
        self.port=port
        self.__retry_seconds=1

    #@Measure.runTime
    def consume(self, event):

        if isinstance(event["data"],list):
            data = ''.join(event["data"])
        else:
            data = event["data"]

        self.submit(data)

        # try:
        #     self.submit(data)
        # except Exception as err:
        #     self.resc
        # while self.loop()==True:
        #     #try:
        #         s=socket.socket()
        #         s.settimeout(1)
        #         s.connect(destination)
        #         self.logging.debug("Writing data to %s"%(str(destination)))
        #         s.sendall(data)
        #         s.close()
        #         break
        #     # except Exception as err:
        #     #     self.logging.warning("Failed to write data to %s. Reason: %s"%(str(destination), err))
        #     #     sleep(1)


    def __doRescue(self, event):

        '''Executes submit.  When submit fails, the inbox is locked and events
        are submitted to the recue queue so they can be dealt with.  The inbox
        is unlocked with an increasing interval of maximum 64 seconds.  The
        advantage of this approach is that the inbox will be empty after a
        while (but rescue queue will be filled).'''

        try:
            self.submit(event)
            self.__retry_seconds=1
        except Exception as err:
            self.warn("Failed to submit data to %s:%s.  Submitting to rescue queue.  Reason: %s"%(self.host, self.port, err))
            self.queuepool.rescue.put(event)
            if self.queuepool.inbox.isLocked() == (False, False):
                self.info("Locking inbox queue.")
                self.queuepool.inbox.putlock()
                self.info("Unlocking inbox in %s seconds"%(self.__retry_seconds))
                spawn_later(self.__retry_seconds, self.__unlockInbox)
                if self.__retry_seconds < 64:
                    self.__retry_seconds*=2

    def __doRepeat(self, event):

        '''Executes submit.  Retries failed submit attempts untill successfull
        with an increasing interval of maximum 64 seconds. Inbox queue is
        locked the moment submit() fails and unlocked when submit() succeeds.
        An arbitrary number of events keep sitting in the inbox queue until
        submit() executes successfully again.'''

        try:
            self.submit(event)
            self.__retry_seconds=1
            #unlock needs to happen here but that's too expensive think about this later.....

        except Exception as err:
            self.warn("Failed to submit data to %s:%s.  Will retry.  Reason: %s"%(self.host, self.port, err))

            self.queuepool.inbox.put(event)
            if self.queuepool.inbox.isLocked() == (False, False):
                self.info("Locking inbox queue.")
                self.queuepool.inbox.putLock()
            self.info("Waiting for %s seconds before retrying."%(self.__retry_seconds))
            sleep(self.__retry_seconds)
            if self.__retry_seconds < 64:
                    self.__retry_seconds*=2


    def __unlockInbox(self):
        self.info("Unlocking inbox.")
        self.queuepool.inbox.putUnlock()

    def shutdown(self):
        self.logging.info('Shutdown')
