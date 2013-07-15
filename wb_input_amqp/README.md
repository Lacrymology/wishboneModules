wb_input_amqp
=============

version: 0.1

**A Wishbone AMQP input module.**

    This module consumes messages from a message broker.

    Each incoming message has a tag which can be submitted to the acknowledge
    queue in order to acknowledge the message with the broker.

    Parameters:

        - name (str):           The instance name when initiated.

        - host (str):           The name or IP of the broker.
                                Default: "localhost"

        - vhost (str):          The virtual host of the broker.
                                Default: "/"

        - username (str):       The username to connect to the broker.
                                Default: "guest"

        - password (str):       The password to connect to the broker.
                                Default: "guest"

        - queue (str):          The queue which should be consumed.
                                Default: A randomly generated queue name.

        - prefetch_count (int): The amount of messages consumed from the queue at once.
                                Default: 1

        - no_ack (bool):        When True, no acknowledgments are done.
                                Default: False

        - auto_create (bool):   When True missing exchanges and queues will be created.
                                Default: True

    Queues:

        - outbox:             Messages arriving from the broker.
        - acknowledge:        Message tags to acknowledge with the broker.
    
