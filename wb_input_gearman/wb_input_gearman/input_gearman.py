#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       gearman.py
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
from gevent import monkey;monkey.patch_all()
from gearman import GearmanWorker
from Crypto.Cipher import AES
import base64

class Gearman(Actor):
    '''
    **A Wishbone input module which consumes jobs from a Gearmand server.**

    Consumes jobs from a Gearmand server.

    Parameters:

        - hostlist(list):   A list of gearmand servers.  Each entry should have
                            format host:port.
                            Default: ["localhost:4730"]

        - secret(str):      The AES encryption key to decrypt Mod_gearman messages.
                            Default: None

        - workers(int):     The number of gearman workers within 1 process.
                            Default: 1

        - queue(str):       The queue to consume jobs from.
                            Default: "wishbone"

    When secret is none, no decryption is done.

    '''

    def __init__(self, name, hostlist=["localhost:4730"], secret=None, workers=1, queue="wishbone"):
        Actor.__init__(self, name, setupbasic=False)
        self.createQueue("outbox")
        self.name = name
        self.hostlist=hostlist
        self.secret=secret
        self.workers=workers
        self.queue=queue

        self.background_instances=[]

        if self.secret == None:
            self.decrypt = self.__plainTextJob
        else:
            key = self.secret[0:32]
            self.cipher=AES.new(key+chr(0)*(32-len(key)))
            self.decrypt = self.__encryptedJob

        self.logging.info ( 'Initiated' )

    def preHook(self):
        for _ in range (self.workers):
            spawn(self.gearmanWorker)

    def consume(self, gearman_worker, gearman_job):
        decrypted = self.decrypt(gearman_job.data)
        self.queuepool.outbox.put({"header":{}, "data":decrypted})
        return "ok"

    def __encryptedJob (self, data):
        return self.cipher.decrypt(base64.b64decode(data))

    def __plainTextJob(self, data):
        return data

    def gearmanWorker(self):

        self.logging.info("Gearmand worker instance started")
        while self.loop():
            try:
                worker_instance=GearmanWorker(self.hostlist)
                worker_instance.register_task(self.queue, self.consume)
                worker_instance.work()
            except Exception as err:
                self.logging.warn ('Connection to gearmand failed. Reason: %s. Retry in 1 second.'%err)
                sleep(1)