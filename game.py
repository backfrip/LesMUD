import logging
import os

import connect
import main

class GameAction(object): # distinguish between actions and events?
    pass

class GameObject(object):
    def __init__(self):
        self.actions = []
        self.context = None

class GameRoute(object):
    pass

class GameServer(object):
    def __init__(self, host, port, debug=False):
        self.actionable = []
        self.avatars = []
        self.connections = []
        
        connect.ThreadedTCPServer.allow_reuse_address = debug
        if debug:
            logging.debug("Server allow_reuse_address is active for debugging purposes!")
        
        self.server = connect.ThreadedTCPServer(
            self, (host, port), connect.ThreadedTCPRequestHandler)
        self.server_thread = connect.make_target_thread(
            self.server.serve_forever)
    
    def run(self):
        while self.server_thread.is_alive():
            line = None
            for connection in self.connections:
                line = connection.readline()
                if line:
                    if line == 'stop':
                        self.stop()
                    else:
                        print("Got:", line.upper())
                        connection.write(line.upper())
            for avatar in self.avatars:
                pass # calculate runtime stats as necessary
            for obj in self.actionable:
                pass # perform queued actions and remove if complete
    
    def stop(self):
        if self.server_thread.is_alive():
            logging.info("Shutting down game server...")
            logging.info("Clearing connections...")
            while self.connections:
                self.connections.pop(0).close()
            logging.info("Connections cleared successfully.")
            self.server.shutdown()
            self.server.server_close()
            logging.info("Game server shutdown successful.")
    
    def add_connection(self, connection):
        connection.avatar = GameObject()
        self.connections.append(connection)
