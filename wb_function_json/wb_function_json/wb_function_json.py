#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       wb_function_json.py
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
from wishbone.errors import QueueLocked
from json import dumps, loads
from jsonschema import Draft3Validator as Validator
from jsonschema import ValidationError


class JSON(Actor):
    '''**A Wishbone module which converts and validates JSON.**

    This module has 2 main modes:

        - Validate JSON data and convert into a Python data structure.
        - Convert a Python data structure into a JSON string.


    Parameters:

        - name (str):   The instance name when initiated.

        - mode (str):   Determines whether the input has to be encoded, decoded or
                        passed through.
                        Can have 3 values: "encode", "decode", "pass"
                        Default: pass

        - schema (str): The filename of the JSON validation schema to load.  When no
                        schema is defined no validation is done.
                        Default: ''

    Queues:

        - inbox:    Incoming events.

        - outbox:   Outgoing events.


    Data which cannot be converted or which fails the validation is purged.
    The schema should be in valid JSON syntax notation. JSON validation can
    only be done on Python objects so you will have to convert your any JSON
    data to a Python object first.
    '''

    def __init__(self, name, mode="pass", schema=''):

        Actor.__init__(self, name, limit=0)
        self.name=name
        self.mode=mode
        self.schema=schema

        if mode == "decode":
            self.convert = self.__loads
        elif mode == "encode":
            self.convert = self.__dumps
        elif mode == "pass":
            self.convert = self.__pass
        else:
            raise Exception ("mode should be either 'encode' or 'decode'.")

        if schema != "":
            self.logging.debug("Validation schema defined.  Doing validation.")
            schema_data = self.__loadValidationSchema(schema)
            self.validate = self.__validate
            self.validator=Validator(schema_data)
        else:
            self.logging.debug("No validation schema defined.  No validation.")
            self.validate = self.__noValidate


    def consume(self, event):

        try:
            event["data"] = self.convert(event["data"])
        except Exception as err:
            self.logging.warn("Unable to convert incoming data. Purged.  Reason: %s"%(err))
            return

        try:
            self.validate(event["data"])
        except ValidationError as err:
            self.logging.warn("JSON data does not pass the validation schema.  Purged.  Reason: %s"%(str(err).replace("\n"," > ")))
            return

        try:
            self.queuepool.outbox.put(event)
        except QueueLocked:
            self.queuepool.inbox.rescue(event)
            self.queuepool.outbox.waitUntillPutAllowed()

    def __loadValidationSchema(self, path):
        with open(path,'r') as schema:
            data = ''.join(schema.readlines())
            print loads(data)
            return loads(data)

    def __loads(self, data):
        return loads(data)

    def __dumps(self, data):
        return dumps(data)

    def __pass(self, data):
        return data

    def __validate(self, data):
        return self.validator.validate(data)

    def __noValidate(self, data):
        return True

    def shutdown(self):
        self.logging.info('Shutdown')
