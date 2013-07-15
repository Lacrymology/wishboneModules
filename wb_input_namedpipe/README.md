wb_input_namedpipe
==================

version: 0.1

**A Wishbone IO module which accepts external input from a named pipe.**

Creates a named pipe to which data can be submitted.

Parameters:

    - name (str):       The instance name when initiated.
    - path (str):       The absolute path of the named pipe.

Queues:

    - inbox:    Data coming from the outside world.
