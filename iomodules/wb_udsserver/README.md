wb_udsserver
============

**A Wishbone IO module which accepts external input from a unix domain socket.**

    Creates a Unix domain socket to which data can be submitted.

    The listener can run in 2 different modes:

        - blob: The incoming data is put into 1 event.
        - line: Each new line is treated as a new event.
    
    When pool is set to True, then path will considered to be directory.  If false,
    then path will be the filename of the socket file.

    Parameters:

        - name (str):           The instance name when initiated.
        - pool (bool):          When true path is considered to be a directory in 
                                which a socket with random name is created.
        - path (str):           The location of the directory or socket file.

    Queues:

        - inbox:       Data coming from the outside world.
    

