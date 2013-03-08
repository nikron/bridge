"""
Wrapper around python API for a logging thread
that listens on a queue, our queue is implemented by
multiprocess Queue.
"""

import logging
import logging.handlers
from multiprocessing import Queue

class LoggingService():
    def __init__(self):
        self.queue = Queue()

        handler = logging.FileHandler('bridge.log')
        formatter = logging.Formatter('%(asctime)s: %(pathname)s - %(levelname)s :: %(msg)s')
        handler.setFormatter(formatter)

        self._queuelistener = logging.handlers.QueueListener(self.queue, handler)

    def start(self):
        self._queuelistener.start()

def service_configure_logging(queue):
    """Configure the root logger to send log records to a queue."""
    handler = logging.handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
