wb_stdout
=========

**The STDOUT Wishbone module is a minimal module which prints each incoming
    event to STDOUT**
    
    After printing the content of the events to STDOUT they are put into the outbox
    queue unless otherwise defined using the purge parameter.  When the complete
    parameter is True, the complete event is printed to STDOUT.  This module should
    only be used for testing or demonstration purposes.    
    
    Parameters:
    
        - name (str):       The instance name when initiated.
        - complete (bool):  When True, print the complete event including headers.
        - purge (bool):     When True the message is dropped and not put in outbox.
        - counter (bool):   Puts an incremental number for each event in front of each event.
    
    Queues:
    
        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    

