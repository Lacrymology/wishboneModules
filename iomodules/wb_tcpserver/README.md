wb_tcpserver
============

**A Wishbone IO module which accepts external input from a TCP socket.**

Creates a TCP socket to which data can be streamed.

Parameters:

    - name (str):           The instance name when initiated.
    - address (str):        The address to bind to.
    - port (int):           The port to bind to.
    - delimiter (str):      The delimiter which separates multiple
                            messages in a stream of data.

Queues:

    - inbox:       Data coming from the outside world.


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
