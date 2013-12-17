wb_output_mqtt
==============

version: 0.2

**A Wishbone output module which writes events to a MQTT broker.**

The module expects to find a <self.name> entry in the header of each event
which contains the topic keyword.

Example header:

    {"header":"mqtt":{"topic":"one/two"}, "data":"testevent"}


Parameters:

    - name (str):       The instance name when initiated.

    - client_id (str):  The client ID
                        default: The PID

    - host(str):        The host to connect to.
                        default: localhost

    - port(int):        The port to connect to.
                        default: 1883

    - keepalive(int):   The keepalive value.
                        default: 60

    - success (bool):   When true stores the event in success queue if
                        send successfully.
                        default: False

    - failed (bool):    When true stores the event in failed queue if
                        not send successfully.
                        default: False


Queues:

    - inbox:    Incoming events.

    - success:  Successful events.

    - failed:   Failed events
