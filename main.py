#!/usr/bin/env python3

import logging
import sys

import connect

if __name__ == "__main__":
    logging.basicConfig(level='DEBUG')
    
    server, server_thread = connect.make_server_thread('0.0.0.0', 26101, debug=True)
    logging.debug("Server allow_reuse_address is active for debugging purposes!")
    stdin, input_thread = connect.make_queue_thread(sys.stdin)
    
    logging.info("Main process now accepting input.")
    while True:
        try:
            line = stdin.readline_nowait()
            if not line:
                pass
            elif line == "exit":
                break
            else:
                logging.info("Unable to parse input.")
        except KeyboardInterrupt:
            print()
            break
    logging.info("Shutting down server...")
    server.shutdown()
    server.server_close()
