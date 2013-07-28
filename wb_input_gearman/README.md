wb_input_gearman
================

version: 0.1

**A Wishbone input module which consumes jobs from a Gearmand server.**

Consumes jobs from a Gearmand server.

Parameters:

    - hostlist(list):   A list of gearmand servers.  Each entry should have
                        format host:port.
                        Default: ["localhost:4730"]

    - secret(str):      The AES encryption key to decrypt Mod_gearman messages.
                        Default: None

    - workers(int):     The number of gearman workers within 1 process.
                        Default: 1

    - queue(str):       The queue to consume jobs from.
                        Default: "wishbone"

When secret is none, no decryption is done.
