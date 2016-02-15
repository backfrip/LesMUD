#!/usr/bin/env python3

import configparser
import json
import logging
import os
import shlex
import sys
from argparse import ArgumentParser
from collections import defaultdict

import connect
import game

class JSONDecoder(json.JSONDecoder):
    pass

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, game.GameObject):
            return # whatever a JSON serialization should look like...
        return json.JSONEncoder.default(self, obj)

def break_loop():
    return True

def command_unrecognized():
    return lambda: print('command unrecognized!')

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
    
    config = configparser.ConfigParser()
    
    logging.basicConfig(level=('DEBUG' if args.debug else 'INFO'))
    
    data_dir = os.path.join(os.path.dirname(__file__), args.data_dir)
    logging.info('Using "{}" for data loading/saving.'.format(data_dir))
    stdin, input_thread = connect.make_queue_thread(sys.stdin)
    
    commands = defaultdict(command_unrecognized)
    for k, v in [('stop', break_loop), ('exit', break_loop)]:
        commands[k] = v
    
    game_server = game.GameServer('0.0.0.0', 26101, debug=args.debug)
    game_server_thread = connect.make_target_thread(target=game_server.run)
    try:
        while game_server_thread.is_alive():
            line = stdin.readline()
            if line:
                line = list(shlex.shlex(line, posix=True))
                if commands[line[0]]():
                    break
    except KeyboardInterrupt:
        print()
    game_server.stop()
    
    logging.info("Exiting...")
