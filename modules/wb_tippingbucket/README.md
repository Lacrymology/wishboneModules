wb_tippingbucket
================

**TippingBucket is a Wishbone module which buffers data.**
    
    This module buffers data and dumps it to the output queue on 2 conditions:

        * Last data enteered in buffer is older than x seconds.
        * Total data in buffer is x size.

    When the buffer is empty, the header of the first incoming message will be used as the header
    for the message going out containing the content of the buffer.  If you want to override that
    header with a predefined one then use the <predefined_header> option.
    
    Disclaimer: The size of the buffer is expressed in bytes.  This is *only* valid when you use
                "single-byte encoding" characters.  Even then it's going to be an approximation.
                When unicode is used this counter is not going to be realistic anymore.
                
    Disclaimer2:    If you require binary data, encode into base64 or
                    something similar.  In that case take the growth of that into account:
                    
                        ~ output_size = ((input_size - 1) / 3) * 4 + 4
                    
                    So 256 bytes binary data results into 344 bytes of Base64 data.
    
    Parameters:

        - age (int):                The time in seconds since the first update when the buffer is flushed.
        - size (int):               The total size in bytes of the buffer when it is flushed.
        - predefined_header (dict): Assign this header to the buffered event when submitting to outbox.
    
    Queues:
    
        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    
    Todo(smetj): Figure out something smarter to find out the size of the buffer.                
    

