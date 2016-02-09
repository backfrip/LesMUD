import logging
from queue import Empty, Queue
from socketserver import StreamRequestHandler, TCPServer, ThreadingMixIn
from socket import SHUT_RDWR
from threading import Thread

class QueueStream(Queue):
    def bridge_line_to(self, dest_queue, decode=None):
        line = self.readline()
        if line:
            if decode:
                line = line.decode(decode)
            dest_queue.put(line)
    
    def readline(self):
        try:
            return self.get_nowait()
        except Empty:
            return None

class ThreadedTCPRequestHandler(StreamRequestHandler):
    def handle(self):
        input_queue, input_thread = make_queue_thread(self.rfile)
        write_queue = QueueStream()
        read_queue = QueueStream()
        self.server.game.add_connection(write_queue, read_queue)
        while input_thread.is_alive():
            input_queue.bridge_line_to(write_queue, decode='utf-8')
            line = read_queue.readline()
            if line:
                self.wfile.write(bytes(line + '\n', 'utf-8'))
    
    def close(self):
        self.connection.shutdown(SHUT_RDWR)
        self.connection.close()

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    def __init__(self, game, *args, **kwargs):
        self.game = game
        super(self.__class__, self).__init__(*args, **kwargs)

def enqueue_thread(read_file, input_queue):
    with read_file:
        for line in read_file:
            input_queue.put(line.strip())

def make_queue_thread(read_file):
    q = QueueStream()
    thread = make_target_thread(enqueue_thread, (read_file, q))
    return (q, thread)

def make_target_thread(target, args=()):
    thread = Thread(target=target, args=args, daemon=True)
    thread.start()
    return thread
