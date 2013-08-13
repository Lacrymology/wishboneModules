wb_output_uds
=============

version: 0.1

**A Wishbone IO module which writes data to a Unix domain socket.**

Writes data to a unix domain socket.


Parameters:

    - name (str):       The instance name when initiated.

    - path (string):    The path to the domain socket.
                        Default: "/tmp/wishbone"

    - stream (bool):    Keep the connection open.
                        Default: False

    - rescue (bool):    When True events which failed to submit
                        successfully are put into the recue queue.
                        Default: False

Queues:

    - inbox:    Incoming events submitted to the outside.
    - rescue:   Contains events which failed to go out succesfully.
