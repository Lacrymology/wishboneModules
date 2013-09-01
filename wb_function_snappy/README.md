wb_function_snappy
==================

version: 0.1

**A Wishbone module which compresses or decompresses data using Snappy.**

This module can be initiated in 2 modes:
    - compress
    - decompress

When initiated in "compress" mode it will compress all incoming data.  When
initiated in "decompress" mode, it will try to decompress all incoming data.

When purge is set to True, incoming events will be dropped when decompression
fails, otherwise it will be forwarded in its original state.

Parameters:

    - name (str):       The instance name when initiated.

    - mode (str):       "compress" or "decompress"
                        default: "compress"

    - purge (bool):     When true then the event will be purged if decompression fails.
                        default: True

Queues:

    - inbox:    Incoming events.

    - outbox:   Outgoing events.
