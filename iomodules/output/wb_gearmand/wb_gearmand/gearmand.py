#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       gearmand.py
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
from gevent import spawn, sleep
from gevent import monkey;monkey.patch_socket()
from gearman import GearmanWorker
from Crypto.Cipher import AES
import base64

class Gearmand(Actor):
    '''
    **A Wishbone IO module which consumes jobs from a Gearmand server.**

    Consumes jobs from a Gearmand server.

    Parameters:

        - hostnames(list):  A list with hostname:port entries.
                            Default: []

        - secret(str):      The AES encryption key to decrypt Mod_gearman messages.
                            Default: None

        - workers(int):     The number of gearman workers within 1 process.
                            Default: 1

    When secret is none, no decryption is done.

    '''

    def __init__(self, name, hostnames=[], secret=None, workers=1):
        Actor.__init__(self, name, limit=0)
        self.name = name
        self.hostnames=hostnames
        self.secret=secret
        self.workers=workers
        key = self.secret[0:32]
        self.cipher=AES.new(key+chr(0)*(32-len(key)))
        self.background_instances=[]
        if self.secret == None:
            self.decode = self.__plainJob
        else:
            self.decode = self.__encryptedJob
        self.logging.info ( 'Initiated' )

    def __encryptedJob (self, gearman_worker, gearman_job):
        self.sendData({'header':{},'data':self.cipher.decrypt(base64.b64decode(gearman_job.data))}, queue='inbox')
        return "ok"

    def __plainJob(self, gearman_worker, gearman_job)
        self.sendData({'header':{},'data':gearman_job.data}, queue='inbox')
        return "ok"

    def start(self):
        self.logging.info('Started')
        for _ in range (self.workers):
            spawn(self.restartOnFailure)

    def restartOnFailure(self):
        while self.loop():
            try:
                worker_instance=GearmanWorker(self.hostnames)
                worker_instance.register_task('perfdata', self.decode)
                worker_instance.work()
            except Exception as err:
                self.logging.warn ('Connection to gearmand failed. Reason: %s'%err)
                sleep(1)

    def shutdown(self):
        self.logging.info('Shutdown')
