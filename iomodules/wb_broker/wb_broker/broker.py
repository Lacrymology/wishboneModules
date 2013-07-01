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

from wishbone import Actor
from gevent import spawn, sleep
from gevent.event import Event
from gevent import monkey;monkey.patch_socket()
import amqp
from amqp.exceptions import NotFound
from amqp.exceptions import ConnectionError

class Broker(Actor):
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
        Actor.__init__(self, name, setupbasic=False, limit=0)
        self.createQueue("inbox")
        self.createQueue("outbox")
        self.createQueue("acknowledge")
        self.registerConsumer(self.produceMessage, self.queuepool.outbox)
        self.registerConsumer(self.acknowledgeMessage, self.queuepool.acknowledge)
        self.name=name
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
        self.exchange_hist={}
        self.queue_hist={}
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
                        self.brokerCreateQueue(self.consume_queue)
                except Exception as err:
                    #sleep_seconds*=2
                    self.logging.critical("AMQP error. Function: %s Reason: %s"%(fn.__name__,err))
                    self.waiter.set()
                sleep(sleep_seconds)
                self.logging.info("Sleeping for %s second."%sleep_seconds)
        return do

    def preHook(self):
        '''
        Initial setup
        '''

        self.setupConnection()
        spawn(self.connectionMonitor)

    @safe
    def setupConnection(self):

        self.queue_hist={}
        self.exchange_hist={}

        #Setup consuming connection
        if self.consume_queue != False:
            self.consumer = amqp.Connection(host="%s:5672"%(self.host), userid=self.username, password=self.password, virtual_host=self.vhost)
            self.consumer_channel = self.consumer.channel()
            self.consumer_channel.basic_qos(prefetch_size=0, prefetch_count=self.prefetch_count, a_global=False)
            self.consumer_channel.basic_consume(queue=self.consume_queue, callback=self.consumeMessage, no_ack=self.no_ack, consumer_tag="incoming")
            self.logging.info('Connected to broker to consume.')

        #Setup producing connection
        self.producer = amqp.Connection(host="%s:5672"%(self.host), userid=self.username, password=self.password, virtual_host=self.vhost)
        self.producer_channel = self.producer.channel()
        self.logging.info('Connected to broker to produce.')

    def connectionMonitor(self):
        while self.loop():
            self.waiter.wait()
            self.setupConnection()
            self.waiter.clear()

    @safe
    def brokerCreateQueue(self, queue_name):
        self.producer_channel.queue_declare(queue=queue_name, auto_delete=False, nowait=False)
        self.logging.info("Creating queue %s"%(queue_name))

    @safe
    def brokerCreateExchange(self, exchange):
        '''Create an exchange.'''
        if exchange != "":
            self.logging.info("Creating exchange %s."%exchange)
            self.producer_channel.exchange_declare(exchange, "direct", auto_delete=False, nowait=False)
        else:
            self.logging.warn("Will not create default exchange.")

    @safe
    def brokerCreateBinding(self,exchange,key):
        '''Create binding between exchange and queue.'''
        if exchange != "":
            self.logging.info("Createing binding between exchange %s and queue %s"%(exchange, key))
            self.producer_channel.queue_bind(key, exchange=exchange, routing_key=key, nowait=False)

    @safe
    def produceMessage(self, message):
        '''Is called upon each event going to the broker infrastructure.'''

        if self.auto_create==True:
            self.createBrokerConfig(message["header"]["broker_exchange"],message["header"]["broker_key"])

        if message["header"].has_key('broker_exchange') and message["header"].has_key('broker_key'):

            if isinstance(message["data"], list):
                data = ''.join(message["data"])
            else:
                data = message["data"]
            msg = amqp.Message(data)
            msg.properties["delivery_mode"] = self.delivery_mode

            self.producer_channel.basic_publish(msg,exchange=message['header']['broker_exchange'],routing_key=message['header']['broker_key'])
            if message['header'].has_key('broker_tag') and self.no_ack == False:
                self.producer_channel.basic_ack(message['header']['broker_tag'])
        else:
            self.logging.warn('Received data for broker without exchange or routing key in header. Purged.')
            if message['header'].has_key('broker_tag') and self.no_ack == False:
                self.producer_channel.basic_ack(message['header']['broker_tag'])

    @safe
    def acknowledgeMessage(self, event):
        self.consumer_channel.basic_ack(event)

    def consumeMessage(self, message):
        '''Is called upon each message coming from the broker infrastructure.'''

        self.queuepool.inbox.put({'header':{'broker_tag':message.delivery_tag},'data':message.body})
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