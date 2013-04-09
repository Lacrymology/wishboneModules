#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tcpserver.py
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
from gevent.queue import Queue
from wishbone.toolkit import QueueFunctions, Block
from uuid import uuid4
import logging


class TCPServer(Greenlet, QueueFunctions, Block):
    '''**A Wishbone IO module which accepts external input from a TCP socket.**

    Creates a TCP socket to which data can be streamed.

    Parameters:

        - name (str):           The instance name when initiated.
        - address (str):        The address to bind to.
        - port (int):           The port to bind to.
        - delimiter (str):      The delimiter which separates multiple
                                messages in a stream of data.

    Queues:

        - inbox:       Data coming from the outside world.


    delimiter
    ~~~~~~~~~

    When no delimiter is defined, all incoming data between connect and
    disconnect is considered to be 1 Wishbone message/event. When a delimiter
    is defined, Wishbone tries to extract multiple events out of a data
    stream.  Wishbone will check each line of data whether it ends with the
    delimiter.  If not the line will be added to an internal buffer.  If so,
    the delimiter will be stripped of and when there is data left, it will be
    added to the buffer after which the buffer will be flushed as one Wishbone
    message/event.  The advantage is that a client can stay connected and
    stream data.
    '''

    def __init__(self, name, port, address='0.0.0.0', delimiter=None):
        Greenlet.__init__(self)
        QueueFunctions.__init__(self)
        Block.__init__(self)
        self.name=name
        self.delimiter=delimiter
        self.logging = logging.getLogger( name )
        self.sock=self.__setupSocket(address, port)
        self.logging.info("TCP server initialized on address %s and port %s."%(address, port))

    def __setupSocket(self, address, port):
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind((address, port))
        sock.listen(50)
        return sock

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
