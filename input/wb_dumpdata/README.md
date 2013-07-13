wb_dumpdata
===========

**A Wishbone IO module which produces 1 batch of x events.**
    
    Generates 1 time upon initialisation a number of events and places them in the inbox queue.
        
    Parameters:

        - name (str):   The instance name when initiated.
        - amount (int): The number of events to produce.
    
    Queues:
    
        - inbox:       "Incoming" generated data.
    

