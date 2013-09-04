wb_output_email
===============

version: 0.1

**A Wishbone module which sends out emails from incoming events.**

Sends emails to a MTA using a provided template.

Parameters:

    - name (str):           The instance name when initiated.

    - mta (string):         The address:port of the MTA to submit the
                            mail to.
                            (default: localhost:25)

    - key (string):         The header key containing the address information.
                            Default: self.name

    - success (bool):       When true stores the event in success queue if
                            send successfully.
                            default: False

    - failed (bool):        When true stores the event in failed queue if
                            not send successfully.
                            default: False


Queues:

    - inbox:    Outgoing events

    - success:  Successful events

    - failed:   Failed events
