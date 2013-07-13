#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       jsonencode.py
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

from wishbone.toolkit import PrimitiveActor
from json import dumps


class JSONEncode(PrimitiveActor):
    '''**A Wishbone module which converts the event payload into a JSON string.**

    Parameters:

        - name (str):    The instance name when initiated.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    '''

    def __init__(self, name):
        PrimitiveActor.__init__(self, name)

    def consume(self, event):
        event["data"] = dumps(event["data"])
        self.putData(event)

    def shutdown(self):
        self.logging.info('Shutdown')
