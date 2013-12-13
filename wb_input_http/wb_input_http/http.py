#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       http.py
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
from gevent import pywsgi, spawn


class HTTP(Actor):
    '''**Receive events over HTTP.**

    This module starts a webserver to which events can be submitted using the
    http protocol.

    Parameters:

        - name (str):       The instance name.

        - address(str):     The address to bind to.
                            Default: 0.0.0.0

        - port(str):        The port to bind to.
                            Default: 10080

        - keyfile(str):     In case of SSL the location of the keyfile to use.
                            Default: None

        - certfile(str):    In case of SSL the location of the certfile to use.
                            Default: None

    Queues:

        - outbox:   Events coming from the outside world and submitted to /


    When more queues are connected to this module instance, they are
    automatically mapped to the URL resource.

    For example http://localhost:10080/fubar is mapped to the <fubar> queue.
    The root resource "/" is mapped the <outbox> queue.
    '''


    def __init__(self, name, address="0.0.0.0", port=10080, keyfile=None, certfile=None, resources=[{"/":"outbox"}]):
        Actor.__init__(self, name)
        self.name=name
        self.address=address
        self.port=port
        self.keyfile=keyfile
        self.certfile=certfile

    def preHook(self):
        spawn(self.__serve)

    def consume(self, env, start_response):

        try:
            for line in env["wsgi.input"].readlines():
                if env['PATH_INFO'] == '/':
                    self.queuepool.outbox.put({"header":{}, "data":line})
                else:
                    getattr(self.queuepool, env['PATH_INFO'].lstrip('/')).put({"header":{}, "data":line})
            start_response('200 OK', [('Content-Type', 'text/html')])
            return "OK"
        except Exception as err:
            start_response('404 Not Found', [('Content-Type', 'text/html')])
            return "A problem occurred processing your request. Reason: %s"%(err)

    def __setupQueues(self):
        return
        self.deleteQueue("inbox")
        for resource in self.resources:
            path=resource.keys()[0]
            queue=resource[resource.keys()[0]]
            self.createQueue(queue)
            self.queue_mapping[path]=getattr(self.queuepool, queue)

    def __serve(self):
        #server = pywsgi.WSGIServer((self.address, self.port), self.consume, keyfile=self.keyfile, certfile=self.certfile)
        self.__server = pywsgi.WSGIServer((self.address, self.port), self.consume, log=None)
        self.__server.start()
        self.logging.info("Serving on %s:%s"%(self.address, self.port))
        self.block()
        self.logging.info("Stopped serving.")
        self.__server.stop()
