wb_output_mongodb
=================

version: 0.1

**A Wishbone output module to write data in MongoDB.**

Parameters:

    - name (str):               The instance name when initiated.

    - host (str):               The name or IP of MongoDB.
                                Default: "localhost"

    - db (str):                 The name of the database.
                                Default: "wishbone"


    - collection (str):         The name of the collection.
                                Default: "wishbone"

    - capped (bool):            If True, creates a capped collection.
                                Default: False


    - size (int):               Maximum size in bytes of the capped collection.
                                Default: 100000

    - max (int):                Maximum number of documents in the capped collection.
                                Default: 100000

    - drop_db(bool):            When True drops the DB after disconnecting.
                                Default: False

Queues:

    - inbox:                    Messages going to MongoDB.
