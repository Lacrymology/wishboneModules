wb_function_msgpack
===================

version: 0.1

**A Wishbone which de/serializes data into or from msgpack format.**

Parameters:

    - name (str):   The instance name when initiated.

    - mode (str):   Determine to serialize or deserialize.
                    Possible values: pack, unpack
                    Default: "pack"

Queues:

    - inbox:    Incoming events.

    - outbox:   Outgoing events.
