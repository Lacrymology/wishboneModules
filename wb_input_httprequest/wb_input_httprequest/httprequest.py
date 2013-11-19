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
from gevent import spawn, sleep, event
from gevent import monkey;monkey.patch_all
import grequests


class HTTPRequest(Actor):
    '''**A HTTP client.**

    This module requests an URL at defined interval.

    Parameters:

        - name (str):       The instance name.

        - url (str/list):   The URL to fetch (including port).
                            Default: http://localhost
                            When a list, will process all urls defined.

        - method(str):      The method to use. (GET)
                            Default: GET

        - data(str):        The string to submit in case of POST, PUT
                            Default: ""

        - username(str):    The login to use.
                            Default: None

        - password(str):    The password to use.
                            Default: None


        - interval(int):    The interval in seconds between each request.
                            Default: 60


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
        self.throttle=event.Event()
        self.throttle.set()

    def preHook(self):
        if isinstance(self.url, list):
            for url in self.url:
                spawn(self.scheduler, url)
        else:
            spawn(self.scheduler, self.url)

    def consume(self, event):
        pass

    def scheduler(self, url):
        while self.loop():
            self.throttle.wait()
            event={"header":{self.name:{}}, "data":None}
            try:
                r = grequests.get(url, auth=(self.username, self.password))
                r.send()
            except Exception as err:
                self.logging.warn("Problem requesting resource.  Reason: %s"%(err))
                sleep(1)
            else:
                event["header"][self.name]["status_code"] = r.status_code
                event["data"]=r.text
                try:
                    self.queuepool.outbox.put(event)
                    sleep(self.interval)
                except QueueLocked:
                    self.queuepool.outbox.waitUntilPutAllowed()

    def enableThrottling(self):
        self.throttle.clear()

    def disableThrottling(self):
        self.throttle.set()

