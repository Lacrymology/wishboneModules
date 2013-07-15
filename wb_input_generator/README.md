wb_input_generator
==================

version: 0.1

**A WishBone IO module which generates random data for testing purposes.**

This module allows you to simulate an incoming data stream with different
characteristics.

Parameters:

    - name (str):               The instance name when initiated.

    - min_payload (int):        The minimum length of each random generated message.
                                default: 1

    - max_payload (int):        The maximum length of each random generated message.
                                default: 1

    - min_interval (int):       The minimum time in seconds between each generated messages.
                                default: 0

    - max_interval (int):       The maximum time in seconds between each generated messages.
                                default: 0.5

    - min_outage_start (int):   The minimum time in seconds the next outage can start.
                                default: 10

    - max_outage_start (int):   The maximum time in seconds the next outage can start.
                                default: 60

    - min_outage_length (int):  The minimum time in seconds an outage can last.
                                default: 0

    - max_outage_length (int):  The maximum time in seconds an outage can last.
                                default: 5

Queues:

    - outbox:    Contains generated data.
