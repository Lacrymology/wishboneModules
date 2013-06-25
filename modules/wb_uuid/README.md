wb_uuid
=======

**A Wishbone module which generates a uuid and adds that value to the header
of each event.**


    Parameters:

        - name (str):    The instance name when initiated.
        - field (str):   The name of the field in the header to assign the
                         value to.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events.


