import logging
import queue
import socket
import socketserver
import threading

class QueueStream(queue.Queue):
    def readline(self):
        try:
            return self.get_nowait()
        except queue.Empty:
            return None

class ThreadedTCPRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        input_queue, input_thread = make_queue_thread(self.rfile)
        while input_thread.is_alive():
            line = input_queue.readline()
            if not line:
                pass
            elif line == b'exit':
                self.close()
            else:
                self.wfile.write(line.upper() + b'\n')
    
    def close(self):
        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass

def enqueue_thread(read_file, input_queue):
    with read_file:
        for line in read_file:
            input_queue.put(line.strip())

def make_queue_thread(read_file):
    q = QueueStream()
    thread = make_target_thread(enqueue_thread, (read_file, q))
    return (q, thread)

def make_target_thread(target, args=()):
    thread = threading.Thread(target=target, args=args, daemon=True)
    thread.start()
    return thread
