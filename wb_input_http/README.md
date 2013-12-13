wb_input_http
=============

version: 0.1

**Receive events over HTTP.**

This module starts a webserver to which events can be submitted using the
http protocol.

Parameters:

    - name (str):       The instance name.

    - address(str):     The address to bind to.
                        Default: 0.0.0.0

    - port(str):        The port to bind to.
                        Default: 10080

    - keyfile(str):     In case of SSL the location of the keyfile to use.
                        Default: None

    - certfile(str):    In case of SSL the location of the certfile to use.
                        Default: None

Queues:

    - outbox:   Events coming from the outside world and submitted to /


When more queues are connected to this module instance, they are
automatically mapped to the URL resource.

For example http://localhost:10080/fubar is mapped to the <fubar> queue.
The root resource "/" is mapped the <outbox> queue.
