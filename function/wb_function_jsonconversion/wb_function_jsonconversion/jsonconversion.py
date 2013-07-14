#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       jsonconversion.py
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
from json import dumps, loads


class JSONConversion(Actor):
    '''**A Wishbone module which converts the event payload into a JSON string.**

    Parameters:

        - name (str):   The instance name when initiated.

        - mode (str):   Determines whether the input has to be encoded or decoded.
                        Can have 2 values: "encode" or "decode".
                        Default: decode

    Queues:

        - inbox:    Incoming events.

        - outbox:   Outgoing (converted) events.
    '''

    def __init__(self, name, mode="decode"):

        Actor.__init__(self, name, limit=0)
        self.name=name
        self.mode=mode

        if mode == "decode":
            self.convert = self.__loads
        elif mode == "encode":
            self.convert = self.__dumps
        else:
            raise Exception ("mode should be either 'encode' or 'decode'.")


    def consume(self, event):

        try:
            event["data"] = self.convert(event["data"])
            self.queuepool.outbox.put(event["data"])
        except Exception as err:
            self.logging.warn("Unable to convert incoming data. Purged.  Reason: %s"%(err))

    def __loads(self, data):
        return loads(data)

    def __dumps(self, data):
        return dumps(data)

    def shutdown(self):
        self.logging.info('Shutdown')
