#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  mongodb.py
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
from gevent import spawn, sleep
from gevent.event import Event
import pymongo
from pymongo.errors import AutoReconnect, CollectionInvalid

class MongoDB(Actor):
    '''**A Wishbone output module to write data in MongoDB.**

    Parameters:

        - name (str):               The instance name when initiated.

        - host (str):               The name or IP of MongoDB.
                                    Default: "localhost"

        - db (str):                 The name of the database.
                                    Default: "wishbone"


        - collection (str):         The name of the collection.
                                    Default: "wishbone"

        - capped (bool):            If True, creates a capped collection.
                                    Default: False


        - size (int):               Maximum size in bytes of the capped collection.
                                    Default: 100000

        - max (int):                Maximum number of documents in the capped collection.
                                    Default: 100000

        - drop_db(bool):            When True drops the DB after disconnecting.
                                    Default: False

    Queues:

        - inbox:                    Messages going to MongoDB.
    '''

    def __init__(self, name, host="localhost", db="wishbone", collection="wishbone", capped=False, size=100000, max=100000, drop_db=False):
        Actor.__init__(self, name, setupbasic=False)
        self.createQueue("inbox",)
        self.createQueue("rescue")
        self.registerConsumer(self.consume, self.queuepool.inbox)
        self.queuepool.inbox.putLock()

        self.name=name
        self.host=host
        self.db=db
        self.collection=collection
        self.capped=capped
        self.size=size
        self.max=max
        self.drop_db=drop_db

        self.mongo=None
        self.connection=None

        self.waiter=Event()
        self.waiter.set()

    def preHook(self):
        '''Creates the capped collection if required.
        '''
        spawn(self.connectionMonitor)

    def connectionMonitor(self):

        while self.loop():
            self.waiter.wait()
            self.queuepool.inbox.putLock()
            (self.connection, self.mongo) = self.setupConnection()
            self.queuepool.inbox.putUnlock()
            self.waiter.clear()

    def setupConnection(self):
        '''Creates a MongoDB connection object and a collection object.
        '''

        while self.loop():
            try:
                connection = pymongo.Connection(self.host, use_greenlets=True)
                self.logging.info("Connected to MongoDB host %s"%(self.host))

                try:
                    if self.capped == True:
                        connection[self.db].create_collection(self.collection, capped=self.capped, size=self.size, max=self.max)
                        self.logging.info("Created capped collection %s in DB %s."%(self.collection, self.db))
                    else:
                        connection[self.db].create_collection(self.collection)
                        self.logging.info("Created collection %s in DB %s."%(self.collection, self.db))
                except CollectionInvalid:
                        self.logging.warn("Collection already exists.  Using that one.")

                return (connection, connection[self.db][self.collection])

            except Exception as err:
                self.logging.warn("Failed to create MongoDB collection.  Reason: %s.  Will retry in 1 second."%(err))
            sleep(1)

    @Measure.runTime
    def consume(self, event):
        try:
            self.mongo.insert(event["data"])
        except Exception as err:
            self.logging.warn('Problem inserting data to MongoDB.  Reason: %s'%(err))
            self.queuepool.rescue.put(event)
            self.waiter.set()

    def postHook(self):
        if self.drop_db == True:
            self.connection.drop_database(self.db)
            self.logging.info('Dropped database %s'%(self.db))
        self.connection.close()
