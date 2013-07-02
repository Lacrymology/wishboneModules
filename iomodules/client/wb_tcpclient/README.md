wb_tcpclient
============

**A Wishbone IO module which writes data to a TCP socket.**

    Writes data to a tcp socket.

    Pool should be a list of strings with format address:port.
    When pool has multiple entries, a random destination will be chosen.

    Parameters:

        - name (str):   The instance name when initiated.
        - pool (list):  A list of addresses:port entries.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events to the outside world.


