wb_jsonvalidator
================

**A Wishbone module which verifies JSON data against a validator schema loaded from file.**
    
    Events consumed from the inbox queue are verified against a Validator schema.  When the event is not a valid JSON document
    or when it doesn't match your predifined Validator schema, it is dropped.

    Parameters:        
    
        - name (str):       The instance name when initiated.    
        - schema (str):     The location and filename of the schema to load.  The schema should follow http://json-schema.org/ specifications.
        - convert (bool):   When True it will aditionally convert the incoming JSON string to a Python object.
        
        
    Queues:        

        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    

