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

    - rescue:   Events which failed to submit.


- The server parameter can have following formats:

    - http://127.0.0.1:9200
    - https://127.0.0.1:9200
    - thrift://127.0.0.1:9500


- The payload event["data"] should be a dictionary.  The pyes
module takes care of any conversion.

- The index and type has to be known when indexing a document.
This module expects these values to be in the header part of
the event:
    {<self.name>:{"index":"value","type":"value"}}
