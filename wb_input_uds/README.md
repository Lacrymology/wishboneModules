wb_input_uds
============

version: 0.1

**A Wishbone input module which listens on a unix domain socket.**

Creates a Unix domain socket to which data can be streamed.

Parameters:

    - name(str):            The instance name when initiated.

    - path(str):            The absolute path of the socket file.

    - delimiter(str):       The delimiter which separates multiple messages in
                            a stream of data.

    - max_connections(int): The number of simultaneous connections allowed.
                            0 means "unlimited".
                            Default: 0

Queues:

    - outbox:   Data coming from the outside world.

delimiter
~~~~~~~~~
When no delimiter is defined (None), all incoming data between connect and disconnect
is considered to be 1 Wishbone message/event.
When a delimiter is defined, Wishbone tries to extract multiple events out of
a data stream.  Wishbone will check each line of data whether it ends with the
delimiter.  If not the line will be added to an internal buffer.  If so, the
delimiter will be stripped of and when there is data left, it will be added to
the buffer after which the buffer will be flushed as one Wishbone
message/event.  The advantage is that a client can stay connected and stream
data.
