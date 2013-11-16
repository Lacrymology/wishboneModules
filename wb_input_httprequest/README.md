wb_input_httprequest
====================

version: 0.1

**A HTTP client.**

This module requests an URL at defined interval.

Parameters:

    - name (str):       The instance name.

    - url (str):        The URL to fetch (including port).
                        Default: http://localhost

    - method(str):      The method to use. (GET)
                        Default: GET

    - data(str):        The string to submit in case of POST, PUT
                        Default: ""

    - username(str):    The login to use.
                        Default: None

    - password(str):    The password to use.
                        Default: None


    - interval(int):    The interval in seconds between each request.
                        Default: 60


Queues:

    - outbox:   Outgoing events.


The header contains:

    - status_code:          The status code of the request.
