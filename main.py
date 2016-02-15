#!/usr/bin/env python3

import logging
import os
import sys
from argparse import ArgumentParser

import connect
import game

data_dir = os.path.dirname(__file__)

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Start a game on the LesMUD engine.")
    # -d --data-dir
    parser.add_argument('-d', '--data-dir', nargs=1, default='./data',
        help='specify a directory from which to save and load game data',
        metavar='path')
    # -v --version
    parser.add_argument('-v', '--version', action='version',
        version='LesMUD Version 0.20')
    # --debug
    parser.add_argument('--debug', action='store_true',
        help='run the game in debug mode')
    args = parser.parse_args()
    
    # args.data_dir == directory from which to save and load game data
    
    logging.basicConfig(level=('DEBUG' if args.debug else 'INFO'))
    
    stdin, input_thread = connect.make_queue_thread(sys.stdin)
    
    game_server = game.GameServer('0.0.0.0', 26101, debug=args.debug)
    game_server_thread = connect.make_target_thread(target=game_server.run)
    try:
        while game_server_thread.is_alive():
            line = stdin.readline()
            if line:
                if line == 'exit' or line == 'stop':
                    break
                else:
                    logging.info("Got: " + line)
    except KeyboardInterrupt:
        print()
    game_server.stop()
    
    logging.info("Exiting...")
