wb_input_json
=============

version: 0.1

**A Wishbone module which converts and validates JSON.**

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
