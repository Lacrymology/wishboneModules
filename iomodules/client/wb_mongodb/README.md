wb_mongodb
==========

**A Wishbone IO which loads messages into a MongoDB.**
            
    Parameters:        

        - name (str):               The instance name when initiated.
        - host (str):               The name or IP of MongoDB.
        - db (str):                 The name of the database.
        - collection (str):         The name of the collection.
        - capped (bool):            Whether the collection is capped.
        - size (int):               Maximum size of the capped collection.
        - max (int):                Maximum number of documents in the capped collection.
        - autodel_db (bool)         Drop the database on exit.
        - dateconversions (list):   A list of fields to convert date.

    Queues:
        
        - outbox:               Messages destined for MongoDB.
    

