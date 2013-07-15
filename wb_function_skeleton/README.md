wb_function_skeleton
====================

version: 0.1

**A bare minimum Wishbone function module.**

This module does nothing more than shoveling the incoming messages to the
outgoing queue without any further modifications.  It can be used as a
base to more complex Wishbone function modules.

Parameters:

    - name (str):    The instance name.

Queues:

    - inbox:    Incoming events.
    - outbox:   Outgoing events.
