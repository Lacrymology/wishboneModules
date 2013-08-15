wb_output_elasticsearch
=======================

version: 0.1

**Output module which writes data into ElasticSearch**

This module writes indexes incoming events to ElasticSearch.

Parameters:

    - name (str):       The instance name.

    - server (str):     The server to connect to and protocol
                        to use.
                        Default: http://127.0.0.1:9200

Queues:

    - inbox:    Incoming events.


- The server parameter can have following formats:

    - http://127.0.0.1:9200
    - https://127.0.0.1:9200
    - thrift://127.0.0.1:9500


- event["data"] is considered to be in JSON format.
- if event["data"] is of type list then the list members are
  considered to be JSON format.
