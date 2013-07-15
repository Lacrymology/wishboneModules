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

from wishbone import Actor
from gevent import spawn, sleep
from gevent.event import Event
from gevent import monkey;monkey.patch_socket()
import amqp
from amqp.exceptions import NotFound
from amqp.exceptions import ConnectionError

class AMQP(Actor):
    '''**A Wishbone AMQP input module.**

    This module consumes messages from a message broker.

    Each incoming message has a tag which can be submitted to the acknowledge
    queue in order to acknowledge the message with the broker.

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

        - queue (str):          The queue which should be consumed.
                                Default: A randomly generated queue name.

        - prefetch_count (int): The amount of messages consumed from the queue at once.
                                Default: 1

        - no_ack (bool):        When True, no acknowledgments are done.
                                Default: False

        - auto_create (bool):   When True missing exchanges and queues will be created.
                                Default: True

    Queues:

        - outbox:             Messages arriving from the broker.
        - acknowledge:        Message tags to acknowledge with the broker.
    '''

    def __init__(self, name, host, vhost='/', username='guest', password='guest', prefetch_count=1, no_ack=True, queue=False, auto_create=True ):
        Actor.__init__(self, name, setupbasic=False, limit=0)
        self.logging.info('Initiated')
        self.createQueue("outbox")
        self.createQueue("acknowledge")
        self.registerConsumer(self.acknowledgeMessage, self.queuepool.acknowledge)
        self.name=name
        self.host=host
        self.vhost=vhost
        self.username=username
        self.password=password
        self.prefetch_count=prefetch_count
        self.no_ack=no_ack
        self.queue = queue
        self.auto_create=auto_create
        self.waiter=Event()
        self.waiter.clear()

    def safe(fn):
        '''decorator function to wrap potentially failing broker IO commands.'''

        def do(self, *args, **kwargs):
            sleep_seconds=1
            while self.loop() == True:
                try:
                    return fn(self, *args, **kwargs)
                except NotFound as err:
                    self.logging.critical("AMQP error. Function: %s Reason: %s"%(fn.__name__,err))
                    if self.auto_create == True:
                        self.brokerCreateQueue(self.queue)
                except Exception as err:
                    #sleep_seconds*=2
                    self.logging.critical("AMQP error. Function: %s Reason: %s"%(fn.__name__,err))
                    self.waiter.set()
                sleep(sleep_seconds)
                sleep()
                self.logging.info("Sleeping for %s second."%sleep_seconds)
        return do

    def preHook(self):
        '''
        Initial setup
        '''

        self.setupConnection()
        spawn(self.drainEvents)

    def drainEvents(self):
        while self.loop():
            try:
                self.consumer_channel.wait()
            except:
                self.setupConnection()

    @safe
    def setupConnection(self):

        self.consumer = amqp.Connection(host="%s:5672"%(self.host), userid=self.username, password=self.password, virtual_host=self.vhost)
        self.consumer_channel = self.consumer.channel()
        self.consumer_channel.basic_qos(prefetch_size=0, prefetch_count=self.prefetch_count, a_global=False)
        self.consumer_channel.basic_consume(queue=self.queue, callback=self.consumeMessage, no_ack=self.no_ack, consumer_tag="incoming")
        self.logging.info('Connected to broker %s to consume queue %s.'%(self.host, self.queue))

    @safe
    def brokerCreateQueue(self, queue_name):
        self.consumer_channel.queue_declare(queue=queue_name, auto_delete=False, nowait=False)
        self.logging.info("Creating queue %s"%(queue_name))

    @safe
    def brokerCreateExchange(self, exchange):
        '''Create an exchange.'''
        if exchange != "":
            self.logging.info("Creating exchange %s."%exchange)
            self.consumer_channel.exchange_declare(exchange, "direct", auto_delete=False, nowait=False)
        else:
            self.logging.warn("Will not create default exchange.")

    @safe
    def brokerCreateBinding(self,exchange,key):
        '''Create binding between exchange and queue.'''
        if exchange != "":
            self.logging.info("Createing binding between exchange %s and queue %s"%(exchange, key))
            self.consumer_channel.queue_bind(key, exchange=exchange, routing_key=key, nowait=False)

    @safe
    def acknowledgeMessage(self, event):
        if "broker_tag" in event["header"]:
            self.consumer_channel.basic_ack(event["header"]["broker_tag"])
        else:
            self.logging.warn("Received a message to acknowledge but no broker_tag found.")

    def consumeMessage(self, message):
        '''Is called upon each message coming from the broker infrastructure.'''

        self.queuepool.outbox.put({'header':{'broker_tag':message.delivery_tag},'data':message.body})
        self.logging.debug('Data received from broker.')

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