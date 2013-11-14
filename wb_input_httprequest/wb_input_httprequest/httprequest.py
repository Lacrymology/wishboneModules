#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       httprequest.py
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
from wishbone.errors import QueueLocked
from gevent import spawn, sleep
from gevent import monkey;monkey.patch_all
import requests


class HTTPRequest(Actor):
    '''**A HTTP client.**

    This module requests an URL at defined interval.

    Parameters:

        - name (str):       The instance name.

        - url (str):        The URL to fetch (including port).
                            Default: http://localhost

        - method(str):      The method to use. (GET, POST, PUT)
                            Default: GET

        - data(str):        The string to submit in case of POST, PUT
                            Default: ""

        - username(str):    The login to use.
                            Default: None

        - password(str):    The password to use.
                            Default: None


        - interval(int):    The interval in seconds between each request.


    Queues:

        - outbox:   Outgoing events.


    The header contains:

        - status_code:          The status code of the request.

    '''


    def __init__(self, name, url="http://localhost", method="GET", data="", username=None, password=None, interval=60):
        Actor.__init__(self, name, setupbasic=False)
        self.createQueue("outbox")
        self.logging.info("Initialized")
        self.url=url
        self.method=method
        self.data=data
        self.username=username
        self.password=password
        self.interval=interval

    def preHook(self):
        spawn(self.scheduler)

    def consume(self, event):
        pass

    def scheduler(self):
        while self.loop():
            event={"header":{self.name:{}}, "data":None}
            r = requests.get(self.url, auth=(self.username, self.password))
            event["header"][self.name]["status_code"] = r.status_code
            event["data"]=r.text
            try:
                self.queuepool.outbox.put(event)
                sleep(self.interval)
            except QueueLocked:
                self.queuepool.outbox.waitUntilPutAllowed()

