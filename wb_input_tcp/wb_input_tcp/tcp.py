#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tcp.py
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
from gevent.server import StreamServer
from gevent.pool import Pool
from gevent import spawn, socket, sleep



class TCP(Actor):
    '''**A Wishbone input module which listens on a TCP socket.**

    Creates a TCP socket to which data can be submitted.

    Parameters:

        - name (str):           The instance name when initiated.

        - address (str):        The address to bind to.
                                Default: "0.0.0.0"

        - port (int):           The port to bind to.
                                Default: 19283

        - delimiter (str):      The delimiter which separates multiple
                                messages in a stream of data.
                                Default: "\n"

        - max_connections(int): The maximum number of simultaneous
                                connections.  0 means "unlimited".
                                Default: 0

        - reuse_port(bool):     Whether or not to set the SO_REUSEPORT
                                socket option.  Interesting when starting
                                multiple instances and allow them to bind
                                to the same port.
                                Requires Linux kernel >= 3.9
                                Default: False


    Queues:

        - outbox:       Data coming from the outside world.


    delimiter
    ~~~~~~~~~

    When no delimiter is defined, all incoming data between connect and
    disconnect is considered to be 1 event. When a delimiter is defined,
    multiple events are extracted out of a data stream using the defined
    delimiter.  The module will check each line of data whether it ends with
    the delimiter.  If not the line will be added to an internal buffer.  If
    so, the delimiter will be stripped of and when there is data left, it will
    be added to the buffer after which the buffer will be flushed as one
    Wishbone message/event.  The advantage is that a client can stay connected
    and stream data.

    Choosing "\n" as a delimiter, which is the default, each new line is a new event.

    '''

    def __init__(self, name, port=19283, address='0.0.0.0', delimiter="\n", max_connections=0, reuse_port=False):
        Actor.__init__(self, name, setupbasic=False)
        self.createQueue("outbox")
        self.name=name
        self.port=port
        self.address=address
        self.delimiter=delimiter
        self.max_connections=max_connections
        self.reuse_port=reuse_port
        if self.delimiter == None:
            self.handle = self.__handleNoDelimiter
        elif self.delimiter == "\n":
            self.handle = self.__handleNextLine
        else:
            self.handle = self.__handleDelimiter

    def preHook(self):
        self.sock=self.__setupSocket(self.address, self.port)
        self.logging.info("TCP server initialized on address %s and port %s."%(self.address, self.port))

    def start(self):
        spawn(self.serve)

    def __setupSocket(self, address, port):
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.reuse_port:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, 15, 1)
        else:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.setblocking(0)
        sock.bind((address, port))
        sock.listen(1)
        return sock

    def __handleNoDelimiter(self, sock, address):
        sfile = sock.makefile()
        chunk = sfile.readlines()
        self.putEvent({'header':{},'data':''.join(chunk)}, self.queuepool.outbox)
        sfile.close()
        sock.close()

    def __handleNextLine(self, sock, address):
        self.logging.debug("Connection from %s."%(str(address[0])))
        sfile = sock.makefile()
        switcher = self.getContextSwitcher(100)

        while switcher():
            chunk = sfile.readline()

            if not chunk:
                self.logging.debug("Client %s disconnected."%(str(address[0])))
                break
            else:
                self.putEvent({'header':{},'data':chunk.rstrip('\r\n')}, self.queuepool.outbox)


    def __handleDelimiter(self, sock, address):
        self.logging.debug("Connection from %s."%(str(address[0])))
        sfile = sock.makefile()
        data=[]
        switcher = self.getContextSwitcher(100)

        while switcher():
            chunk = sfile.readline()

            if not chunk:
                if len(data) > 0:
                    self.putEvent({'header':{},'data':''.join(data)}, self.queuepool.outbox)
                self.logging.debug("Client %s disconnected."%(str(address[0])))
                break

            elif chunk.endswith(self.delimiter):
                chunk=chunk.rstrip(self.delimiter)
                if chunk != '':
                    data.append(chunk)
                    self.putEvent({'header':{},'data':''.join(data)}, self.queuepool.outbox)
                    data=[]
            else:
                data.append(chunk)

        sfile.close()
        sock.close()

    def serve(self):
        if self.max_connections > 0:
            pool = Pool(self.max_connections)
            self.logging.debug("Setting up a connection pool of %s connections."%(self.max_connections))
            self.stream_server = StreamServer(self.sock, self.handle, spawn=pool)
            self.stream_server.start()
        else:
            self.stream_server = StreamServer(self.sock, self.handle)
            self.stream_server.start()
        self.block()

    def enableThrottling(self):
        self.stream_server.stop_accepting()

    def disableThrottling(self):
        self.stream_server.start_accepting()

    def shutdown(self):
        self.logging.info('Shutdown')
