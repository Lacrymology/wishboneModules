wb_broker
=========

**A Wishbone IO module which handles AMQP input and output.**

    This module handles the IO from and to a message broker.  This module has
    specifically been tested against RabbitMQ.  The module is meant to be resilient
    against disconnects and broker unavailability.

    The module will currently not create any missing queues or exchanges.

    Acknowledging can can done in 2 ways:

    - Messages which arrive to outbox and which have an acknowledge tag in the header
      will be acknowledged with the broker.

    - When a broker_tag is submitted to the "acknowledge" queue using sendRaw(),
      then the message will be acknowledged at the broker.

    All incoming messages should have at least following header:

        {'header':{'broker_exchange':name, 'broker_key':name, 'broker_tag':tag}}

        - broker_exchange:    The exchange to which data should be submitted.
        - broker_key:         The routing key used when submitting data.
        - broker_tag:         The tag used to acknowledge the message from the broker.

    Parameters:

        - name (str):           The instance name when initiated.
        - host (str):           The name or IP of the broker.
        - vhost (str):          The virtual host of the broker. By default this is '/'.
        - username (str):       The username to connect to the broker.  By default this is 'guest'.
        - password (str):       The password to connect to the broker.  By default this is 'guest'.
        - consume_queue (str):  The queue which should be consumed. By default this is "wishbone_in".
        - prefetch_count (str): The amount of messages consumed from the queue at once.
        - no_ack (str):         No acknowledgements required? By default this is False (means acknowledgements are required.)
        - delivery_mode (int):  The message delivery mode.  1 is Non-persistent, 2 is Persistent. Default=2
        - auto_create (bool):   When True missing exchanges and queues will be created.

    Queues:

        - inbox:              Messages coming from the broker.
        - outbox:             Messages destined for the broker.
        - acknowledge:        Message tags to acknowledge with the broker.
    

