#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  broker.py
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

import logging
from wishbone.toolkit import QueueFunctions, Block, TimeFunctions
from gevent import Greenlet, spawn, sleep
import amqp
from amqp.exceptions import NotFound
from amqp.exceptions import ConnectionError
from gevent import monkey;monkey.patch_all()

class Broker(Greenlet, QueueFunctions, Block, TimeFunctions):
    '''**A Wishbone IO module which handles AMQP input and output.**

    This module handles the IO from and to a message broker.  This module has
    specifically been tested against RabbitMQ.  The module is meant to be resilient
    against disconnects and broker unavailability.

    The module will currently not create any missing queues or exchanges.

    Acknowledging can can done in 2 ways:

    - Messages which arrive to outbox and which have an acknowledge tag in the header
      will be acknowledged with the broker.

    - When a broker_tag is submitted to the "acknowledge" queue using sendRaw(),
      then the message will be acknowledged at the broker.

    All incoming messages should have at least following header:

        {'header':{'broker_exchange':name, 'broker_key':name, 'broker_tag':tag}}

        - broker_exchange:    The exchange to which data should be submitted.
        - broker_key:         The routing key used when submitting data.
        - broker_tag:         The tag used to acknowledge the message from the broker.

    Miscellaneous:

        Outgoing Events (submitted to outbox) with a data field of <type list> will be joined into 1 string.
        All other data fields are converted into <type str>.


    Parameters:

        - name (str):           The instance name when initiated.
        - host (str):           The name or IP of the broker.
        - vhost (str):          The virtual host of the broker. By default this is '/'.
        - username (str):       The username to connect to the broker.  By default this is 'guest'.
        - password (str):       The password to connect to the broker.  By default this is 'guest'.
        - consume_queue (str):  The queue which should be consumed. By default this is False. When False no queue is consumed.
        - prefetch_count (str): The amount of messages consumed from the queue at once.
        - no_ack (str):         No acknowledgments required? By default this is False (means acknowledgments are required.)
        - delivery_mode (int):  The message delivery mode.  1 is Non-persistent, 2 is Persistent. Default=2
        - auto_create (bool):   When True missing exchanges and queues will be created.

    Queues:

        - inbox:              Messages coming from the broker.
        - outbox:             Messages destined for the broker.
        - acknowledge:        Message tags to acknowledge with the broker.
    '''

    def __init__(self, name, host, vhost='/', username='guest', password='guest', prefetch_count=1, no_ack=True, consume_queue=False, delivery_mode=2, auto_create=True ):

        Greenlet.__init__(self)
        Block.__init__(self)
        QueueFunctions.__init__(self)
        self.name=name
        self.logging = logging.getLogger( self.name )
        self.logging.info('Initiated')
        self.host=host
        self.vhost=vhost
        self.username=username
        self.password=password
        self.prefetch_count=prefetch_count
        self.no_ack=no_ack
        self.consume_queue = consume_queue
        self.delivery_mode=delivery_mode
        self.auto_create=auto_create
        self.queue_hist={}
        self.exchange_hist={}
        self.createQueue("acknowledge")

    def safe(fn):
        '''decorator function to wrap potentially failing broker IO commands.'''

        def do(self, *args, **kwargs):
            sleep_seconds=1
            while self.block() == True:
                try:
                    fn(self, *args, **kwargs)
                    break
                except NotFound as err:
                    self.logging.error("AMQP error. Function: %s Reason: %s"%(fn.__name__,err))
                    if self.auto_create == True:
                        self.brokerCreateQueue(kwargs["consume_queue"])
                except ConnectionError as err:
                    sleep_seconds*=2
                    self.logging.error("AMQP error. Function: %s Reason: %s"%(fn.__name__,err))
                except Exception as err:
                    sleep_seconds*=2
                    self.logging.error("AMQP error. Function: %s Reason: %s"%(fn.__name__,err))
                sleep(sleep_seconds)
                self.logging.info("Sleeping for %s seconds."%sleep_seconds)
        return do

    def _run(self):
        '''Blocking function which start consumption and producing of data.  It is executed when issuing the Greenlet start()'''

        self.logging.info('Started')
        self.brokerSetupConnection(host=self.host, username=self.username, password=self.password, virtual_host=self.vhost,
            prefetch_count=self.prefetch_count,consume_queue=self.consume_queue,no_ack=self.no_ack
        )
        outgoing = spawn(self.continuousProduceBroker)
        ack = spawn(self.continuousAcknowledgeBroker)

        if self.consume_queue != False:
            self.continuousConsumeBroker()
        else:
            self.wait()

    def continuousConsumeBroker(self):
        '''Blocking function which consumes all data from the defined broker queue.'''

        while self.block() == True:
            while self.incoming.callbacks:
                self.incoming.wait()
            sleep(0.1)

    def continuousProduceBroker(self):
        '''Submits all data from self.outbox into the broker by calling the produce() funtion untill interrupted.'''

        while self.block() == True:
            self.brokerProduceMessage(self.getData("outbox"))

    def continuousAcknowledgeBroker(self):
        '''A blocking function which continuously consumes the "acknowledge" queue untill interrupted.'''

        while self.block() == True:
            self.brokerAcknowledgeMessage(self.getData("acknowledge"))

    @safe
    def brokerSetupConnection(self,host,username,password,virtual_host,prefetch_count,consume_queue,no_ack):
        '''Handles connection and channel creation.  Blocks and retries untill successful or interrupted.'''

        self.conn = amqp.Connection(host="%s:5672"%(host), userid=username, password=password, virtual_host=virtual_host)
        if consume_queue != False:
            self.incoming = self.conn.channel()
            self.incoming.basic_qos(prefetch_size=0, prefetch_count=prefetch_count, a_global=False)
            self.incoming.basic_consume(queue=consume_queue, callback=self.brokerConsumeMessage, no_ack=no_ack, consumer_tag="incoming")
        else:
            self.logging.debug("No queue to consume defined hence not consuming anything.")
        self.outgoing = self.conn.channel()
        self.logging.info('Connected to broker')

    @safe
    def brokerCreateQueue(self, queue_name):
        admin = self.conn.channel()
        admin.queue_declare( queue=queue_name, auto_delete=False, nowait=True)
        admin.close()
        self.logging.info("Creating queue %s"%(queue_name))

    @safe
    def brokerCreateExchange(self, exchange):
        '''Create an exchange.'''
        if exchange != "":
            self.logging.info("Creating exchange %s."%exchange)
            self.outgoing.exchange_declare(exchange, "direct", auto_delete=False, nowait=True)
        else:
            self.logging.warn("Will not create default exchange.")

    @safe
    def brokerCreateBinding(self,exchange,key):
        '''Create binding between exchange and queue.'''
        if exchange != "":
            self.logging.info("Createing binding between exchange %s and queue %s"%(exchange, key))
            self.outgoing.queue_bind(key, exchange=exchange, routing_key=key, nowait=True)

    @safe
    @TimeFunctions.do
    def brokerAcknowledgeMessage(self, ack):
        self.incoming.basic_ack(ack)

    @safe
    @TimeFunctions.do
    def brokerProduceMessage(self,message):
        '''Is called upon each message going to the broker infrastructure.'''

        if self.auto_create==True:
            self.createBrokerConfig(message["header"]["broker_exchange"],message["header"]["broker_key"])

        if message["header"].has_key('broker_exchange') and message["header"].has_key('broker_key'):

            if isinstance(message["data"], list):
                data = ''.join(message["data"])
            else:
                data = message["data"]
            msg = amqp.Message(data)
            msg.properties["delivery_mode"] = self.delivery_mode

            self.outgoing.basic_publish(msg,exchange=message['header']['broker_exchange'],routing_key=message['header']['broker_key'])
            if message['header'].has_key('broker_tag') and self.no_ack == False:
                self.brokerAcknowledgeMessage(message['header']['broker_tag'])
        else:
            self.logging.warn('Received data for broker without exchange or routing key in header. Purged.')
            if message['header'].has_key('broker_tag') and self.no_ack == False:
                self.brokerAcknowledgeMessage(message['header']['broker_tag'])

    def createBrokerConfig(self, exchange, key):
        '''Create the provided exchange a queue with the keyname and binding.'''

        if not exchange in self.exchange_hist:
            self.exchange_hist[exchange]=True
            self.brokerCreateExchange(exchange)

        if not key in self.queue_hist:
            self.queue_hist[key]=True
            self.brokerCreateQueue(key)
            self.brokerCreateBinding(exchange,key)

    @TimeFunctions.do
    def brokerConsumeMessage(self,message):
        '''Is called upon each message coming from the broker infrastructure.'''

        self.putData({'header':{'broker_tag':message.delivery_tag},'data':message.body}, queue='inbox')
        self.logging.debug('Data received from broker.')
        sleep()

    def shutdown(self):
        '''This function is called on shutdown().'''
        try:
             self.incoming.close()
             self.outgoing.close()
        except:
            pass
        self.logging.info('Shutdown')
