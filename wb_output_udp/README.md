wb_output_udp
=============

version: 0.1

**A Wishbone IO module to submit data over UDP.**

Write data to a UDP socket.

Parameters:

    - name (str):       The instance name when initiated.

    - host (string):    The host to submit to.
                        Default: "localhost"

    - port (int):       The port to submit to.
                        Default: 19283

Queues:

    - inbox:    Incoming events submitted to the outside.
