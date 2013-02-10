wb_brokerheader
===============

**A Wishbone module which adds a wishbone.io_modules.broker header to each
    event**.

    When events go to the outside world via the boker module, it must know which
    exchange and routing key to use.  Typically one would connect this outbox queue
    to the outboxqueue of the wishbone.io_modules.broker instance.

    Parameters:

        - name (str):       The instance name when initiated.
        - key (str):        The routing key to use.
        - exchange (str):   The exchange to use.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    
