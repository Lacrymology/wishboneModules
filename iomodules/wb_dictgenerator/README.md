wb_dictgenerator
================

**A WishBone IO module which generates dictionaries build out of words randomly
chosen from a provided wordlist.**
    
    This module allows you to generate an incoming stream of dictionaries.

    Parameters:
        
        - name (str):       The instance name when initiated.
        - wordlist (str):   The absolute path of a wordlist.
        - min_keys (int):   The minimum number of elements per dictionary.
        - max_keys (int):   The maximum number of elements per dictionary.
        
    Queues:
    
        - inbox:    "Incoming" data produced by DictGenerator itself.    
