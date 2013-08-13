wb_output_tcp
=============

version: 0.1

**A Wishbone IO module which writes data to a TCP socket.**

Writes data to a tcp socket.

Parameters:

    - name (str):       The instance name when initiated.

    - host (string):    The host to submit to.
                        Default: "localhost"

    - port (int):       The port to submit to.
                        Default: 19283

    - timeout(int):     The time in seconds to timeout when
                        connecting
                        Default: 1

    - stream (bool):    Keep the connection open.
                        Default: False

    - rescue (bool):    When True events which failed to submit
                        successfully are put into the recue queue.
                        Default: False

Queues:

    - inbox:    Incoming events submitted to the outside.
    - rescue:   Contains events which failed to go out succesfully.
