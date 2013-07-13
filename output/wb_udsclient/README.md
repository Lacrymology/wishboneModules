wb_udsclient
============

**A Wishbone IO module which writes data into a Unix domain socket.**

    Writes data into a Unix domain socket.  
    
    If pool is True, path is expected to be a directory containing socket files over
    which the module will spread outgoing events.
    If pool if False, path is a socket file to which all outgoing events will be
    submitted.
        
    Parameters:

        - name (str):   The instance name when initiated.
        - pool (bool):  When True expects path to be a pool of sockets.        
        - path (str):   The absolute path of the socket file or the socket pool.
        
    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events destined to the outside world.
    

