wb_output_amqp
==============

**A Wishbone AMQP output module.**

    This module produces messages to an AMQP message broker.

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
        - delivery_mode (int):  The message delivery mode.  1 is Non-persistent, 2 is Persistent. Default=2
        - auto_create (bool):   When True missing exchanges and queues will be created.

    Queues:

        - inbox:              Messages to the broker.