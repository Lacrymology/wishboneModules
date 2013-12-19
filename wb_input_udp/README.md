wb_input_udp
============

version: 0.2.1

**A Wishbone module which handles UDP input.**


Parameters:

    - name(str):        The name you want this module to be registered under.

    - address(str):     The address to bind to.
                        Default: "0.0.0.0"

    - port(int):        The port on which the server should listen.
                        default: 19283

    - reuse_port(bool): Whether or not to set the SO_REUSEPORT socket option.
                        Allows multiple instances to bind to the same port.
                        Requires Linux kernel >= 3.9
                        Default: False



Queues:

    - outbox:   Contains incoming events
