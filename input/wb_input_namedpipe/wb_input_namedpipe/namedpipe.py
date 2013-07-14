#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  namedpipeserver.py
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
from gevent import spawn, sleep
#from gevent import monkey;monkey.patch_all()
import os


class NamedPipe(Actor):
    '''**A Wishbone IO module which accepts external input from a named pipe.**

    Creates a named pipe to which data can be submitted.

    Parameters:

        - name (str):       The instance name when initiated.
        - path (str):       The absolute path of the named pipe.

    Queues:

        - inbox:    Data coming from the outside world.
    '''

    __version__ = 0.1

    def __init__(self, name, path="/tmp/%s.namedpipe"%(os.getpid())):
        Actor.__init__(self, name, setupbasic=False, limit=0)
        self.createQueue("outbox")
        self.name=name
        self.path = path
        self.logging.info('Initialiazed.')

    def preHook(self):

        os.mkfifo ( self.path )
        self.logging.info('Named pipe %s created.'%(self.path))
        self.fd = os.open(self.path, os.O_RDONLY|os.O_NONBLOCK)
        spawn(self.serve)

    def serve(self):
        '''Reads the named pipe.'''

        #todo(smetj):   ideally hub.loop.stat should be used as a watcher but
        #               that is not working in pypy for the moment.

        self.logging.info('Started.')
        while self.loopContextSwitch():
            try:
                lines = os.read(self.fd, 4096).splitlines()
            except OSError:
                pass
            else:
                if len(lines) > 0:
                    for line in  lines:
                        self.queuepool.outbox.put({'header':{},'data':line})
                else:
                    sleep(0.1)

    def shutdown(self):
        self.fifo.close()
        os.unlink(self.path)
        self.logging.info('Shutdown')

