#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       generator.py
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
from string import ascii_uppercase, ascii_lowercase, digits
from random import choice, uniform, randint
from gevent import spawn, sleep, spawn_later
from gevent.event import Event
from time import time, strftime, localtime


class Generator(Actor):

    '''**A WishBone IO module which generates random data for testing purposes.**

    This module allows you to simulate an incoming data stream with different
    characteristics.

    Parameters:

        - name (str):               The instance name when initiated.

        - min_payload (int):        The minimum length of each random generated message.
                                    default: 1

        - max_payload (int):        The maximum length of each random generated message.
                                    default: 1

        - min_interval (int):       The minimum time in seconds between each generated messages.
                                    default: 0

        - max_interval (int):       The maximum time in seconds between each generated messages.
                                    default: 0.5

        - min_outage_start (int):   The minimum time in seconds the next outage can start.
                                    default: 10

        - max_outage_start (int):   The maximum time in seconds the next outage can start.
                                    default: 60

        - min_outage_length (int):  The minimum time in seconds an outage can last.
                                    default: 0

        - max_outage_length (int):  The maximum time in seconds an outage can last.
                                    default: 5

    Queues:

        - outbox:    Contains generated data.
    '''

    def __init__(self, name, min_payload=1, max_payload=1, min_interval=0, max_interval=0.5, min_outage_start=10, max_outage_start=60, min_outage_length=0, max_outage_length=5):
        Actor.__init__(self, name, setupbasic=False)
        self.createQueue("temp")
        self.createQueue("outbox")
        self.registerConsumer(self.consume, self.queuepool.temp)

        self.name = name
        self.min_payload=min_payload
        self.max_payload=max_payload
        self.min_interval=min_interval
        self.max_interval=max_interval
        self.min_outage_start=min_outage_start
        self.max_outage_start=max_outage_start
        self.min_outage_length=min_outage_length
        self.max_outage_length=max_outage_length
        self.outage=Event()
        self.outage.set()

    def preHook(self):
        spawn(self.go)
        self.planOutage()

    def go(self):
        self.logging.info('Started')

        while self.loopContextSwitch():
            random_string = ''.join(choice(ascii_uppercase + ascii_lowercase + digits) for x in range(self.min_payload)+range(randint(0, self.max_payload)))
            self.logging.debug('Data batch generated with size of %s bytes.'%len(random_string))
            self.queuepool.temp.put({"header":{},"data":random_string})

            sleeping_time = uniform(self.min_interval,self.max_interval)
            self.logging.debug('Waiting for %s seconds until the next data batch is generated.'%sleeping_time)
            sleep(sleeping_time)

    def consume(self, event):
        self.outage.wait()
        self.putEvent(event, self.queuepool.outbox)

    def planOutage(self):
        '''Plans when the next outage will occur.'''

        start_outage=uniform(self.min_outage_start, self.max_outage_start)
        spawn_later(start_outage,self.executeOutage)
        self.logging.info('Next outage is planned at %s'%(strftime("%a, %d %b %Y %H:%M:%S +0000", localtime(time()+start_outage))))

    def executeOutage(self):
        '''Executes the outage by locking the <consume> function.'''

        self.outage.clear()
        outage_length=uniform(self.min_outage_length, self.max_outage_length)
        self.logging.info("Outage of %s seconds started."%(outage_length))
        sleep(outage_length)
        self.logging.info("Outage finished.")
        self.planOutage()
        self.outage.set()