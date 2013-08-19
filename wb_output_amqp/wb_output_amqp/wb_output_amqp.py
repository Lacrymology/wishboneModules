#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wb_amqp.py
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

from gevent import monkey;monkey.patch_socket()
from wishbone import Actor
from gevent import spawn, sleep
from gevent.event import Event
import amqp
from amqp.exceptions import NotFound
from amqp.exceptions import ConnectionError

class AMQP(Actor):
    '''**A Wishbone AMQP output module.**

    This module produces messages to an AMQP message broker.

    All incoming messages should have at least following header:

        {<self.name>:{'broker_exchange':name, 'broker_key':name, 'broker_tag':tag}}

        - broker_exchange:    The exchange to which data should be submitted.
        - broker_key:         The routing key used when submitting data.
        - broker_tag:         The tag used to acknowledge the message from the broker.

    Parameters:

        - name (str):           The instance name when initiated.

        - host (str):           The name or IP of the broker.
                                Default: "localhost"

        - vhost (str):          The virtual host of the broker.
                                Default: "/"

        - username (str):       The username to connect to the broker.
                                Default: "guest"

        - password (str):       The password to connect to the broker.
                                Default: "guest"

        - delivery_mode(int):   The message delivery mode.  1 is Non-persistent, 2 is Persistent.
                                Default: 2

        - auto_create (bool):   When True missing exchanges and queues will be created.
                                Default: True

    Queues:

        - inbox:    Events to the broker.

        - rescue:   Events which failed to submit.
    '''

    def __init__(self, name, host, vhost='/', username='guest', password='guest', delivery_mode=2, auto_create=True ):
        Actor.__init__(self, name, setupbasic=False, limit=0)
        self.createQueue("inbox")
        self.queuepool.inbox.putLock()
        self.createQueue("rescue")
        self.registerConsumer(self.produceMessage, self.queuepool.inbox)
        self.name=name
        self.logging.info('Initiated')
        self.host=host
        self.vhost=vhost
        self.username=username
        self.password=password
        self.delivery_mode=delivery_mode
        self.auto_create=auto_create
        self.exchange_hist={}
        self.queue_hist={}
        self.waiter=Event()
        self.waiter.set()

    def preHook(self):
        '''Initial setup'''

        spawn(self.connectionMonitor)

    def connectionMonitor(self):
        '''Tries to initiate a connection to the AMQP broker.'''

        while self.loop():
            self.waiter.wait()
            while self.loop():
                try:
                    self.setupConnection()
                    self.queuepool.inbox.putUnlock()
                    self.waiter.clear()
                    break
                except Exception as err:
                    self.logging.warning("Failed to establish connection to %s.  Retry in 1 second."%(self.host))
                    sleep(1)
            self.waiter.clear()

    def setupConnection(self):

        self.queue_hist={}
        self.exchange_hist={}

        #Setup producing connection
        self.producer = amqp.Connection(host="%s:5672"%(self.host), userid=self.username, password=self.password, virtual_host=self.vhost)
        self.producer_channel = self.producer.channel()
        self.logging.info('Connected to broker.')

    def brokerCreateQueue(self, queue_name):
        self.producer_channel.queue_declare(queue=queue_name, auto_delete=False, nowait=False)
        self.logging.info("Creating queue %s"%(queue_name))

    def brokerCreateExchange(self, exchange):
        '''Create an exchange.'''
        if exchange != "":
            self.logging.info("Creating exchange %s."%exchange)
            self.producer_channel.exchange_declare(exchange, "direct", auto_delete=False, nowait=False)
        else:
            self.logging.warn("Will not create default exchange.")

    def brokerCreateBinding(self,exchange,key):
        '''Create binding between exchange and queue.'''
        if exchange != "":
            self.logging.info("Creating binding between exchange %s and queue %s"%(exchange, key))
            self.producer_channel.queue_bind(key, exchange=exchange, routing_key=key, nowait=False)

    def produceMessage(self, message):
        '''Is called upon each event going to the broker infrastructure.'''

        try:
            if self.auto_create==True:
                self.createBrokerConfig(message["header"][self.name]["broker_exchange"],message["header"][self.name]["broker_key"])
            if isinstance(message["data"], list):
                data = ''.join(message["data"])
            else:
                data = message["data"]
            msg = amqp.Message(data)
            msg.properties["delivery_mode"] = self.delivery_mode
            self.producer_channel.basic_publish(msg,exchange=message['header'][self.name]['broker_exchange'],routing_key=message['header'][self.name]['broker_key'])
        except KeyError as err:
            self.logging.warn("Event purged.  Header is missing information.  Reason: %s"%(err))
        except Exception as err:
            self.logging.debug("Failed to submit event to broker.  Reason: %s"%(err))
            self.waiter.set()
            self.queuepool.inbox.putLock()
            self.queuepool.rescue.put(message)

    def createBrokerConfig(self, exchange, key):
        '''Create the provided exchange a queue with the keyname and binding.'''

        if not exchange in self.exchange_hist:
            self.exchange_hist[exchange]=True
            self.brokerCreateExchange(exchange)

        if not key in self.queue_hist:
            self.queue_hist[key]=True
            self.brokerCreateQueue(key)
            self.brokerCreateBinding(exchange,key)

    def shutdown(self):
        '''This function is called on shutdown().'''
        try:
             self.incoming.close()
             self.outgoing.close()
        except:
            pass
        self.logging.info('Shutdown')