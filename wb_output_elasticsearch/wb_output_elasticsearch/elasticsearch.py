#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       elasticsearch.py
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

from gevent import monkey;monkey.patch_all
import pyes
from wishbone import Actor
from gevent import sleep
from gevent import spawn


class ElasticSearch(Actor):
    '''**Output module which writes data into ElasticSearch**

    This module writes indexes incoming events to ElasticSearch.

    Parameters:

        - name (str):       The instance name.

        - server (str):     The server to connect to and protocol
                            to use.
                            Default: http://127.0.0.1:9200

    Queues:

        - inbox:    Incoming events.


    - The server parameter can have following formats:

        - http://127.0.0.1:9200
        - https://127.0.0.1:9200
        - thrift://127.0.0.1:9500


    - event["data"] is considered to be in JSON format.
    - if event["data"] is of type list then the list members are
      considered to be JSON format.

    '''

    def __init__(self, name, server="http://127.0.0.1:9200", ):
        Actor.__init__(self, name, setupbasic=True, limit=0)
        self.createQueue("rescue")
        self.server=server
        self.logging.info("Initialized")
        self.queuepool.inbox.putLock()
        self.conn=self.getConnection()
        self.__connecting=False

    def preHook(self):

        spawn(self.connectionMonitor)

    def consume(self, event):

        try:
            self.conn.index(event["data"], event["header"]["index"], event["header"]["type"])
        except Exception as err:
            self.logging.warn("Unable to index document.  Reason: %s"%(err))
            self.queuepool.rescue.put(event)
            sleep(1)

    def getConnection(self):
        return pyes.ES(self.server)

    def connectionMonitor(self):
        """creates self.conn
        """

        while self.loop():
            if self.conn.collect_info() != True:
                self.logging.warn("Could not connect to %s."%(self.server))
                self.queuepool.inbox.putLock()
                self.conn=self.getConnection()
            else:
                self.queuepool.inbox.putUnlock()
            sleep(1)