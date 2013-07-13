wb_input_uds
============

**A Wishbone input module which listens on a unix domain socket.**

    Creates a Unix domain socket to which data can be streamed.

    Parameters:

        - name (str):           The instance name when initiated.
        - pool (bool):          When true path is considered to be a directory in
                                which a socket with random name is created.
        - path (str):           The location of the directory or socket file.
        - delimiter (str):      The delimiter which separates multiple messages in
                                a stream of data.

    Queues:

        - inbox:       Data coming from the outside world.

    pool
    ~~~~
    When pool is set to True, the path value will be considered a directory.
    This module will then create a socket file with a random name in it.
    When pool is set to False, then path value will be considered the filename of
    the socket file.
    When multiple, parallel instances are started we would have the different
    domain socket servers bind to the same name, which will not work.  Creating a
    random name inside a directory created a pool of sockets to which a client can
    round-robin.

    delimiter
    ~~~~~~~~~
    When no delimiter is defined, all incoming data between connect and disconnect
    is considered to be 1 Wishbone message/event.
    When a delimiter is defined, Wishbone tries to extract multiple events out of
    a data stream.  Wishbone will check each line of data whether it ends with the
    delimiter.  If not the line will be added to an internal buffer.  If so, the
    delimiter will be stripped of and when there is data left, it will be added to
    the buffer after which the buffer will be flushed as one Wishbone
    message/event.  The advantage is that a client can stay connected and stream
    data.