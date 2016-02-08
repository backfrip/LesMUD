#!/usr/bin/env python3

import argparse
import logging
import sys

import connect

class GameServer(object):
    def __init__(self, host, port, debug=False):
        connect.ThreadedTCPServer.allow_reuse_address = debug
        if debug:
            logging.debug("Server allow_reuse_address is active for debugging purposes!")
        self.server = connect.ThreadedTCPServer(
            (host, port), connect.ThreadedTCPRequestHandler)
        self.server_thread = connect.make_target_thread(
            self.server.serve_forever)
    
    def stop(self):
        logging.info("Game server shutting down...")
        self.server.shutdown()
        self.server.server_close()

def main(debug=False):
    logging.basicConfig(level='DEBUG')
    
    game_server = GameServer('0.0.0.0', 26101, debug=debug)
    
    stdin, input_thread = connect.make_queue_thread(sys.stdin)
    
    logging.info("Main process now accepting input.")
    while True:
        try:
            line = stdin.readline()
            if line:
                if line == "exit":
                    break
                else:
                    logging.info("Unable to parse input.")
        except KeyboardInterrupt:
            print()
            break
    logging.info("Shutting down game server...")
    game_server.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Start a game on the LesMUD engine.")
    parser.add_argument('-v', '--version', action='version',
        version='LesMUD Version 0.12')
    parser.add_argument('--debug', action='store_true',
        help='run the game in debug mode')
    args = parser.parse_args()
    
    main(debug=args.debug)
