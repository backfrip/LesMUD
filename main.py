#!/usr/bin/env python3

import logging
import sys
from argparse import ArgumentParser

import connect

class GameServer(object):
    def __init__(self, host, port, stdq, debug=False):
        connect.ThreadedTCPServer.allow_reuse_address = debug
        if debug:
            logging.debug("Server allow_reuse_address is active for debugging purposes!")
        self.server = connect.ThreadedTCPServer(
            self, (host, port), connect.ThreadedTCPRequestHandler)
        self.server_thread = connect.make_target_thread(
            self.server.serve_forever)
        self.stdq = stdq
        self.connections = []
    
    def add_connection(self, read_queue, write_queue):
        self.connections.append((read_queue, write_queue))
    
    def run(self):
        while self.server_thread.is_alive():
            line = self.stdq.readline()
            if line:
                if line == 'exit' or line == 'stop':
                    self.stop()
                else:
                    print(line.upper())
            for connection in self.connections:
                line = connection[0].readline()
                if line:
                    if line == 'stop':
                        self.stop()
                    else:
                        print("Got:", line.upper())
                        connection[1].put(line.upper())
    
    def stop(self):
        if self.server_thread.is_alive():
            logging.info("Shutting down game server...")
            self.server.shutdown()
            self.server.server_close()

def main(debug=False):
    logging.basicConfig(level=('DEBUG' if debug else 'INFO'))
    
    game_queue = connect.QueueStream()
    game_server = GameServer('0.0.0.0', 26101, game_queue, debug=debug)
    game_server_thread = connect.make_target_thread(
        target=game_server.run)
    
    stdin, input_thread = connect.make_queue_thread(sys.stdin)
    
    logging.info("Main process now accepting input.")
    try:
        while game_server_thread.is_alive():
            stdin.bridge_line_to(game_queue)
    except KeyboardInterrupt:
        print()
    logging.info("Main process no longer accepting input.")
    game_server.stop()
    logging.info("Shut down successfully.")
    logging.info("Exiting...")

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Start a game on the LesMUD engine.")
    parser.add_argument('-v', '--version', action='version',
        version='LesMUD Version 0.12')
    parser.add_argument('--debug', action='store_true',
        help='run the game in debug mode')
    args = parser.parse_args()
    
    main(debug=args.debug)
