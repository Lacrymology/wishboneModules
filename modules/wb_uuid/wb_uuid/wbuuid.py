#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       wbuuid.py
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
from uuid import uuid4

class WBUUID(PrimitiveActor):
    '''**A Wishbone module which adds a uuid value to the header.**


    Parameters:

        - name (str):   The instance name when initiated.
        - field(str):   The name of the field to contain the UUID.
                        (default "uuid")
        - body(bool):   If true adds the key/value to the ["data"]
                        part on the condition it is a dictionary.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    '''

    def __init__(self, name, field="uuid", body=False):
        PrimitiveActor.__init__(self, name)
        self.name=name
        self.field=field
        self.body=body

    def consume(self, event):
        value = str(uuid4())
        event["header"][self.field] = value
        if self.body == True:
            if isinstance(event["data"], dict):
                event["data"][self.field] = value
        self.putData(event)

    def shutdown(self):
        self.logging.info('Shutdown')
