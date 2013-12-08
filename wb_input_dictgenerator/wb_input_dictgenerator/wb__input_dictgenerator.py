#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       dictgenerator.py
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

from random import choice, uniform, randint
from gevent import sleep, spawn
from wishbone import Actor
from wishbone.errors import QueueLocked, QueueFull

class DictGenerator(Actor):

    '''**A WishBone input module which generates dictionaries build out of words randomly
    chosen from a provided wordlist.**

    This module allows you to generate an incoming stream of dictionaries.

    Parameters:

        - name (str):               The instance name when initiated.
        - filename (str):           The absolute path+filename of a wordlist.
        - randomize_keys (bool):    If true randomizes the keys.  Otherwise keys are sequential numbers.
        - num_values (bool):        If true values will be numeric and randomized.
        - num_values_min (int):     The minimum of a value when they are numeric.
        - num_values_max (int):     The maximum of a value when they are numeric.
        - min_elements (int):       The minimum number of elements per dictionary.
        - max_elements (int):       The maximum number of elements per dictionary.
        - sleep (int):              The time in seconds to sleep between each message.


    Queues:

        - outbox:    Contains the generated dictionaries.


    When no filename is provided and internal wordlist is used.
    '''

    def __init__(self, name, filename=None, randomize_keys=True, num_values=False, num_values_min=0, num_values_max=1, min_elements=1, max_elements=1, sleep=0 ):
        Actor.__init__(self, name, setupbasic=False)
        self.createQueue("outbox")
        self.name = name
        self.filename=filename
        self.randomize_keys=randomize_keys
        self.num_values=num_values
        self.num_values_min=num_values_min
        self.num_values_max=num_values_max
        self.min_elements=min_elements
        self.max_elements=max_elements
        self.wordlist=self.readWordList(self.filename)
        self.sleep=sleep

        self.key_number=-1

        if self.randomize_keys == True:
            self.generateKey = self.pickWord
        else:
            self.generateKey = self.generateKeyNumber

        if self.num_values == True:
            self.generateValue = self.generateValueNumber
        else:
            self.generateValue = self.pickWord


    def start(self):
        self.logging.info('Started')
        if self.sleep > 0:
            spawn(self.__startGeneratingSleep)
        else:
            spawn(self.__startGeneratingNoSleep)

    def __startGeneratingSleep(self):
        switcher = self.getContextSwitcher(100)

        while switcher():
            data={}
            for x in xrange(0, randint(self.min_elements,self.max_elements)):
                data[self.generateKey()]=self.generateValue()
            sleep(self.sleep)
            self.putEvent({"header":{},"data":data}, self.queuepool.outbox)
            self.key_number=-1

    def __startGeneratingNoSleep(self):

        switcher = self.getContextSwitcher(100)
        while switcher():
            data={}
            for x in xrange(0, randint(self.min_elements,self.max_elements)):
                data[self.generateKey()]=self.generateValue()
            self.putEvent({"header":{},"data":data}, self.queuepool.outbox)
            self.key_number=-1

    def readWordList(self, filename):
        '''Reads and returns the wordlist as a tuple.'''

        if filename == None:
            from wb_input_dictgenerator import brit_a_z
            return brit_a_z.wordlist
        else:
            f = open(filename,"r")
            words=f.readlines()
            f.close()
            return tuple(words)

    def pickWord(self):
        '''Returns a word as string from the wordlist.'''

        while self.loop():
            word = choice(self.wordlist).rstrip()
            try:
                return word.encode("ascii","ignore")
            except:
                pass

    def generateValueInteger(self):
        '''Returns a random number.'''
        return randint(self.num_values_min,self.num_values_max)

    def generateKeyNumber(self):
        '''Generates a key by incrementing integer.'''
        self.key_number +=1
        return str(self.key_number)

    def shutdown(self):
        self.logging.info('Shutdown')
