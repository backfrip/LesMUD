import logging
from queue import Empty, Queue
from socketserver import StreamRequestHandler, TCPServer, ThreadingMixIn
from socket import SHUT_RDWR
from threading import Thread

class QueueStream(Queue):
    def __init__(self, *args, encoding=None, **kwargs):
        if encoding:
            def get_nowait():
                return super(self.__class__, self).get_nowait(
                    ).decode(encoding)
            self.get_nowait = get_nowait
        super(self.__class__, self).__init__(*args, **kwargs)
    
    def readline(self):
        try:
            return self.get_nowait()
        except Empty:
            return None

class ThreadedTCPRequestHandler(StreamRequestHandler):
    def handle(self):
        self.avatar = None
        self.read_queue, input_thread = make_queue_thread(
            self.rfile, encoding='utf-8')
        self.write_queue = QueueStream()
        self.server.game.add_connection(self)
        while input_thread.is_alive():
            line = self.write_queue.readline()
            if line:
                self.wfile.write(bytes(line + '\n', 'utf-8'))
    
    def close(self):
        self.connection.shutdown(SHUT_RDWR)
        self.connection.close()
    
    def readline(self):
        return self.read_queue.readline()
    
    def write(self, output):
        self.write_queue.put(output)

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    def __init__(self, game, *args, **kwargs):
        self.game = game
        super(self.__class__, self).__init__(*args, **kwargs)

def enqueue_thread(read_file, input_queue):
    with read_file:
        for line in read_file:
            input_queue.put(line.strip())

def make_queue_thread(read_file, encoding=None):
    q = QueueStream(encoding=encoding)
    thread = make_target_thread(enqueue_thread, (read_file, q))
    return (q, thread)

def make_target_thread(target, args=()):
    thread = Thread(target=target, args=args, daemon=True)
    thread.start()
    return thread
