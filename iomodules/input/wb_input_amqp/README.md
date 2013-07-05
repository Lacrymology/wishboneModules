wb_input_amqp
=============

**A Wishbone AMQP input module.**

    This module consumes messages from a message broker.

    Each incoming message has a tag which can be submitted to the acknowledge
    queue in order to acknowledge the message with the broker.

    Parameters:

        - name (str):           The instance name when initiated.
        - host (str):           The name or IP of the broker.
        - vhost (str):          The virtual host of the broker. By default this is '/'.
        - username (str):       The username to connect to the broker.  By default this is 'guest'.
        - password (str):       The password to connect to the broker.  By default this is 'guest'.
        - consume_queue (str):  The queue which should be consumed. By default this is False. When False no queue is consumed.
        - prefetch_count (str): The amount of messages consumed from the queue at once.
        - no_ack (str):         No acknowledgments required? By default this is False (means acknowledgments are required.)
        - auto_create (bool):   When True missing exchanges and queues will be created.

    Queues:

        - outbox:             Messages coming from the broker.
        - acknowledge:        Message tags to acknowledge with the broker.