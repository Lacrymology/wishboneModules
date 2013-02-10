wb_tcpclient
============

**A Wishbone IO module which writes data to a TCP socket.**

    Writes data to a tcp socket.  
    
    If pool is True, path is expected to be a directory containing socket files over
    which the module will spread outgoing events.
    
    If pool if False, path is a socket file to which all outgoing events will be
    submitted.
        
    Parameters:

        - name (str):   The instance name when initiated.
        - pool (list):  A list of addresses:port entries to which data needs to be submitted.
                        Currently a destination is chosen randomly.  More setups will follow.
        
    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events destined to the outside world.
    

