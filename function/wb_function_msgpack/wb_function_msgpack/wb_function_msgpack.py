#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       wb_function_msgpack.py
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
import msgpack


class Msgpack(Actor):
    '''**A Wishbone which de/serializes data into or from msgpack format.**

    Parameters:

        - name (str):   The instance name when initiated.
        - mode (str):   Determine to serialize or deserialize.
                        Possible values: pack, unpack

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    '''

    __version__ = 0.1

    def __init__(self, name, mode):
        Actor.__init__(self, name, limit=0)
        if mode == "pack":
            self.do = self.pack
        elif mode == "unpack":
            self.do = self.unpack
        else:
            raise Exception("mode should either be 'pack' or 'unpack'")

    def pack(self, data):

        return msgpack.packb(data)

    def unpack(self, data):

        return msgpack.unpackb(data)

    def consume(self,event):
        event["data"]=self.do(event["data"])
        self.queuepool.outbox.put(event)

    def shutdown(self):
        self.logging.info('Shutdown')
