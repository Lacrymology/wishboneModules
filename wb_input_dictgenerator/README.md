wb_input_dictgenerator
======================

version: 0.2

**A WishBone input module which generates dictionaries build out of words randomly
chosen from a provided wordlist.**

This module allows you to generate an incoming stream of dictionaries.

Parameters:

    - name (str):               The instance name when initiated.
    - filename (str):           The absolute path+filename of a wordlist.
    - randomize_keys (bool):    If true randomizes the keys.  Otherwise keys are sequential numbers.
    - num_values (bool):        If true values will be numeric and randomized.
    - num_values_min (int):     The minimum of a value when they are numeric.
    - num_values_max (int):     The maximum of a value when they are numeric.
    - min_elements (int):       The minimum number of elements per dictionary.
    - max_elements (int):       The maximum number of elements per dictionary.
    - sleep (int):              The time in seconds to sleep between each message.


Queues:

    - outbox:    Contains the generated dictionaries.


When no filename is provided and internal wordlist is used.
