wb_output_tcp_parallel
======================

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

    - delimiter(str):   A delimiter to add to each event.
                        Default: "\n"

    - success (bool):   When True, submits succesfully outgoing
                        events to the 'success' queue.
                        Default: False

    - failed (bool):    When True, submits failed outgoing
                        events to the 'failed' queue.
                        Default: False

    - block(bool):      When False, it doesn't stop events from
                        entering the inbox queue.
                        Default: True

Queues:

    - inbox:    Incoming events submitted to the outside.

    - success:  Contains events which went out succesfully.
                (optional)

    - failed:   Contains events which did not go out successfully.
                (optional)
