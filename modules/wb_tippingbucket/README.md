wb_tippingbucket
================

**TippingBucket is a Wishbone module which buffers data.**

    This module buffers data and dumps it to the output queue on 3 conditions:

        * Last data entered in buffer exceeds <age> seconds.
        * The length of the data in buffer exceeds <size> size.
        * Number of incoming events exceeds <events>.

    When the buffer is empty, the header of the first incoming message will be
    used as the header for the message going out containing the content of the
    buffer.  If you want to override that header with a predefined one then
    use the <predefined_header> option.

    Keep in mind to set at least one of the parameters otherwise buffering
    will be indefinite until your box runs out of memory


    Parameters:

        - age (int):    The time in seconds to buffer before flushing.
                        0 to disable. (default 0)
        - size (int):   The total size in bytes to buffer before flushing.
                        0 to disable. (default 0)
        - events (int): The total number of events to buffer before flushing.
                        0 to disable. (default 0)

        - predefined_header (dict): Assign this header to the buffered event
                                    when submitting to outbox.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events.
