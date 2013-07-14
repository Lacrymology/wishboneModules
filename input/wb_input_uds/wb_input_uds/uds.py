#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  udsserver.py
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
from os import remove, path, makedirs, getpid
from gevent.server import StreamServer
from gevent import socket, sleep, spawn
from gevent.pool import Pool

class UDS(Actor):
    '''**A Wishbone input module which listens on a unix domain socket.**

    Creates a Unix domain socket to which data can be streamed.

    Parameters:

        - name(str):            The instance name when initiated.

        - path(str):            The absolute path of the socket file.

        - delimiter(str):       The delimiter which separates multiple messages in
                                a stream of data.

        - max_connections(int): The number of simultaneous connections allowed.
                                0 means "unlimited".
                                Default: 0

    Queues:

        - outbox:   Data coming from the outside world.

    delimiter
    ~~~~~~~~~
    When no delimiter is defined (None), all incoming data between connect and disconnect
    is considered to be 1 Wishbone message/event.
    When a delimiter is defined, Wishbone tries to extract multiple events out of
    a data stream.  Wishbone will check each line of data whether it ends with the
    delimiter.  If not the line will be added to an internal buffer.  If so, the
    delimiter will be stripped of and when there is data left, it will be added to
    the buffer after which the buffer will be flushed as one Wishbone
    message/event.  The advantage is that a client can stay connected and stream
    data.
    '''

    __version__ = 0.1

    def __init__(self, name, path="/tmp/%s.socket"%(getpid()), delimiter=None, max_connections=0):
        Actor.__init__(self, name, setupbasic=False, limit=0)
        self.createQueue("outbox")
        self.name=name
        self.path=path
        self.delimiter=delimiter
        self.max_connections=max_connections
        self.logging.info("Initialiazed")

    def preHook(self):
        (self.sock, self.filename)=self.__setupSocket(self.path)
        self.logging.info("UDS server listening on path %s."%(self.path))

    def __setupSocket(self, path):
        sock=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind(path)
        sock.listen(50)
        self.logging.info("Socket file %s created."%path)
        return (sock, path)

    def handle(self, sock, address):
        sfile = sock.makefile()
        data=[]

        if self.delimiter == None:
            chunk = sfile.readlines()
            self.queuepool.outbox.put({'header':{},'data':''.join(chunk)})
        else:
            while self.block()==True:
                chunk = sfile.readline()
                if chunk == "":
                    if len(data) > 0:
                        self.queuepool.outbox.put({'header':{},'data':''.join(data)})
                    break
                else:
                    if chunk.endswith(self.delimiter):
                        chunk=chunk.rstrip(self.delimiter)
                        if chunk != '':
                            data.append(chunk)
                        if len(data) > 0:
                            self.queuepool.outbox.put({'header':{},'data':''.join(data)})
                            data=[]
                    else:
                        data.append(chunk)
        sfile.close()
        sock.close()


    def start(self):
        spawn(self.serve)

    def serve(self):
        if self.max_connections > 0:
            pool = Pool(self.pool)
            StreamServer(self.sock, self.handle, spawn=pool).start()
        else:
            StreamServer(self.sock, self.handle).start()
        self.block()

    def postHook(self):
        remove(self.path)