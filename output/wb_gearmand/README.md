wb_gearmand
===========


    ***Consumes jobs from a Gearmand server.***
    
    Consumes jobs from a Gearmand server.
    
    Parameters:
        * hostnames:    A list with hostname:port entries.
                        Default: []
                        Type: List

        * secret:   The AES encryption key to decrypt Mod_gearman messages.
                    Default: ''
                    Type: String

        * workers:  The number of gearman workers within 1 process.
                    Default: 1
                    Type: Int
    

