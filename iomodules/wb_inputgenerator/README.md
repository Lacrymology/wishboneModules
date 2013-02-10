wb_inputgenerator
=================

**A WishBone IO module which generates random data for testing purposes.**
    
    This module allows you to simulate an incoming data stream without acutally 
    having to produce any data yourself.

    Parameters:
        
        - name (str):               The instance name when initiated.
        - min_payload (int):        The minimum length of each random generated message.
        - max_payload (int):        The maximum length of each random generated message.
        - min_interval (int):       The minimum time in seconds between each generated messages.
        - max_interval (int):       The maximum time in seconds between each generated messages.
        - min_outage_start (int):   The minimum time in seconds the next outage can start.
        - max_outage_start (int):   The maximum time in seconds the next outage can start.
        - min_outage_length (int):  The minimum time in seconds an outage can last.
        - max_outage_length (int):  The maximum time in seconds an outage can last.
        
    Queues:
    
        - inbox:    "Incoming" data produced by InputGenerator itself.    
    

