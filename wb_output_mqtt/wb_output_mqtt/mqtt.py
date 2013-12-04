#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       snappy.py
#
#       Copyright 2013 Jelle Smet development@smetj.net
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

from wishbone import Actor
from wishbone.errors import QueueLocked, QueueFull
from gevent import monkey;monkey.patch_all(socket=True, dns=True, select=True)
from gevent import spawn, sleep
from gevent.event import Event
import mosquitto

class MQTT(Actor):
    '''**A Wishbone output module which writes events to a MQTT broker.**

    The module expects to find a <self.name> entry in the header of each event
    which contains the topic keyword.

    Example header:

        {"header":"mqtt":{"topic":"one/two"}, "data":"testevent"}


    Parameters:

        - name (str):       The instance name when initiated.

        - client_id (str):  The client ID
                            default: The PID

        - host(str):        The host to connect to.
                            default: localhost

        - port(int):        The port to connect to.
                            default: 1883

        - keepalive(int):   The keepalive value.
                            default: 60

        - success (bool):   When true stores the event in success queue if
                            send successfully.
                            default: False

        - failed (bool):    When true stores the event in failed queue if
                            not send successfully.
                            default: False


    Queues:

        - inbox:    Incoming events.

        - success:  Successful events.

        - failed:   Failed events
    '''

    def __init__(self, name, client_id=None, host="127.0.0.1", port=1883, keepalive=60, success=False, failed=False):
        Actor.__init__(self, name, setupbasic=False)
        self.createQueue("inbox")
        self.registerConsumer(self.consume,self.queuepool.inbox)
        self.name=name
        self.client_id=client_id
        self.host=host
        self.port=port
        self.keepalive=keepalive
        self.queuepool.inbox.putLock()
        self.__connect=Event()
        self.__connect.set()

        if success == True:
            self.createQueue("success")
            self.doSuccess=self.__doSuccess
        else:
            self.doSuccess=self.__doNoSuccess

        if failed == True:
            self.createQueue("failed")
            self.doFailed=self.__doFailed
        else:
            self.doFailed=self.__doNoFailed

    def preHook(self):
        spawn(self.connectionMonitor)
        spawn(self.loopMonitor)

    def consume(self, event):
        try:
            self.__client.publish(event["header"][self.name]["topic"], str(event["data"]), 0)
            self.doSuccess(event)
        except KeyError as err:
            self.logging.err("Event did not have the required header key: %s. Purged."%(err))
        except Exception as err:
            self.logging.err("Failed to submit message to broker.  Reason: %s"%(err))
            self.doFailed(event)
            self.__connect.set()
            self.queuepool.inbox.putLock()

    def loopMonitor(self):
        while self.loop():
            if self.__client.loop() != 0:
                self.queuepool.inbox.putLock()
                self.__connect.set()
            else:
                self.queuepool.inbox.putUnlock()
            sleep(1)

    def connectionMonitor(self):

        self.__client=mosquitto.Mosquitto(self.client_id, clean_session=True)

        while self.loop():
            self.__connect.wait()
            try:
                self.__client.connect(self.host, self.port, self.keepalive)
                self.__connect.clear()
            except Exception as err:
                self.logging.err("Problem connecting to MQTT broker.  Reason: %s"%(err))
            sleep(1)

    def postHook(self):
        self.__client.disconnect()

    def __doSuccess(self, event):
        self.queuepool.success.put(event)

    def __doNoSuccess(self, event):
        pass

    def __doFailed(self, event):
        self.queuepool.failed.put(event)

    def __doNoFailed(self, event):
        self.queuepool.inbox.rescue(event)