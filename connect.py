import logging
import queue
import socket
import socketserver
import threading

class Connection(object):
    def __init__(self):
        

class ConnectionManager(object):
    def __init__(self):
        self.counter = 0
        self.connections = []
    
    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            self.counter++
            return self.connections[self.counter]
        except IndexError:
            self.counter = 1
            return self.connections

class QueueStream(queue.Queue):
    def readline_nowait(self):
        try:
            return self.get_nowait()
        except queue.Empty:
            return None

class ThreadedTCPRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        input_queue, input_thread = make_queue_thread(self.rfile)
        while input_thread.is_alive():
            line = input_queue.readline_nowait()
            if not line:
                pass
            elif line == b'exit':
                self.force_close()
            else:
                self.wfile.write(line.upper() + b'\n')
    
    def force_close(self):
        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass

def enqueue_thread(read_file, input_queue):
    with read_file:
        for line in read_file:
            input_queue.put(line.strip())

def make_queue_thread(read_file):
    q = QueueStream()
    thread = threading.Thread(target=enqueue_thread, args=(read_file, q))
    thread.daemon = True
    thread.start()
    return (q, thread)

def make_server_thread(host, port, debug=False):
    ThreadedTCPServer.allow_reuse_address = debug
    server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target = server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return (server, server_thread)
