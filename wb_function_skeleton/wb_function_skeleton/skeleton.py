#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       skeleton.py
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


class Skeleton(Actor):
    '''**A bare minimum Wishbone function module.**

    This module does nothing more than shoveling the incoming messages to the
    outgoing queue without any further modifications.  It can be used as a
    base to more complex Wishbone function modules.

    Parameters:

        - name (str):    The instance name.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    '''

    __version__ = 0.1

    def __init__(self, name):
        Actor.__init__(self, name, setupbasic=True, limit=0)
        self.logging.info("Initialized")

    def consume(self, event):
        self.queuepool.outbox.put(event)