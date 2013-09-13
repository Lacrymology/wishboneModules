wb_input_tcp
============

version: 0.1

**A Wishbone input module which listens on a TCP socket.**

Creates a TCP socket to which data can be submitted.

Parameters:

    - name (str):           The instance name when initiated.

    - address (str):        The address to bind to.
                            Default: "0.0.0.0"

    - port (int):           The port to bind to.
                            Default: 19283

    - delimiter (str):      The delimiter which separates multiple
                            messages in a stream of data.
                            Default: None

    - max_connections(int): The maximum number of simultaneous
                            connections.  0 means "unlimited".
                            Default: 0

    - reuse_port(bool):     Whether or not to set the SO_REUSEPORT
                            socket option.  Interesting when starting
                            multiple instances and allow them to bind
                            to the same port.
                            Default: False


Queues:

    - outbox:       Data coming from the outside world.


delimiter
~~~~~~~~~

When no delimiter is defined, all incoming data between connect and
disconnect is considered to be 1 Wishbone message/event. When a delimiter
is defined, Wishbone tries to extract multiple events out of a data
stream.  Wishbone will check each line of data whether it ends with the
delimiter.  If not the line will be added to an internal buffer.  If so,
the delimiter will be stripped of and when there is data left, it will be
added to the buffer after which the buffer will be flushed as one Wishbone
message/event.  The advantage is that a client can stay connected and
stream data.
