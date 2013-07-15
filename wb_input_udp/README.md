wb_input_udp
============

version: 0.1

**A Wishbone module which handles UDP input.**


Parameters:

    - name(str):        The name you want this module to be registered under.

    - address(str):     The address to bind to.
                        Default: "0.0.0.0"

    - port(int):        The port on which the server should listen.
                        default: 19283


Queues:

    - outbox:   Contains incoming events
