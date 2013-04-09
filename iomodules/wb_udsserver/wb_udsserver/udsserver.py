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

from os import remove, path, makedirs
from gevent.server import StreamServer
from gevent import Greenlet, socket, sleep
from wishbone.toolkit import QueueFunctions, Block
from uuid import uuid4
import logging


class UDSServer(Greenlet, QueueFunctions, Block):
    '''**A Wishbone IO module which accepts external input from a unix domain socket.**

    Creates a Unix domain socket to which data can be streamed.

    Parameters:

        - name (str):           The instance name when initiated.
        - pool (bool):          When true path is considered to be a directory in
                                which a socket with random name is created.
        - path (str):           The location of the directory or socket file.
        - delimiter (str):      The delimiter which separates multiple messages in
                                a stream of data.

    Queues:

        - inbox:       Data coming from the outside world.

    pool
    ~~~~
    When pool is set to True, the path value will be considered a directory.
    This module will then create a socket file with a random name in it.
    When pool is set to False, then path value will be considered the filename of
    the socket file.
    When multiple, parallel instances are started we would have the different
    domain socket servers bind to the same name, which will not work.  Creating a
    random name inside a directory created a pool of sockets to which a client can
    round-robin.

    delimiter
    ~~~~~~~~~
    When no delimiter is defined, all incoming data between connect and disconnect
    is considered to be 1 Wishbone message/event.
    When a delimiter is defined, Wishbone tries to extract multiple events out of
    a data stream.  Wishbone will check each line of data whether it ends with the
    delimiter.  If not the line will be added to an internal buffer.  If so, the
    delimiter will be stripped of and when there is data left, it will be added to
    the buffer after which the buffer will be flushed as one Wishbone
    message/event.  The advantage is that a client can stay connected and stream
    data.
    '''

    def __init__(self, name, pool=True, path="/tmp", delimiter=None):
        Greenlet.__init__(self)
        QueueFunctions.__init__(self)
        Block.__init__(self)
        self.name=name
        self.pool=pool
        self.path=path
        self.delimiter=delimiter
        self.logging = logging.getLogger( name )
        (self.sock, self.filename)=self.__setupSocket()
        self.logging.info("Initialiazed")

    def __setupSocket(self):
        if self.pool == True:
            if not path.exists(self.path):
                makedirs(self.path)
            filename = "%s/%s"%(self.path,uuid4())
            self.logging.info("Socket pool %s created."%filename)
        else:
            filename = self.path
            self.logging.info("Socket file %s created."%filename)

        sock=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind(filename)
        sock.listen(50)
        return (sock, filename)

    def handle(self, sock, address):
        sfile = sock.makefile()
        data=[]

        if self.delimiter == None:
            chunk = sfile.readlines()
            self.putData({'header':{},'data':''.join(chunk)}, queue='inbox')
        else:
            while self.block()==True:
                chunk = sfile.readline()
                if chunk == "":
                    if len(data) > 0:
                        self.putData({'header':{},'data':''.join(data)}, queue='inbox')
                    break
                else:
                    if chunk.endswith(self.delimiter):
                        chunk=chunk.rstrip(self.delimiter)
                        if chunk != '':
                            data.append(chunk)
                        if len(data) > 0:
                            self.putData({'header':{},'data':''.join(data)}, queue='inbox')
                            data=[]
                    else:
                        data.append(chunk)
        sfile.close()
        sock.close()

    def _run(self):
        try:
            StreamServer(self.sock, self.handle).serve_forever()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        remove(self.filename)
        self.logging.info('Shutdown')
