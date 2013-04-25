"""
Wrapper around python API for a logging thread that listens on a queue;
the queue we use is the multiprocessing Queue for obvious reasons.
"""

import logging
import logging.handlers
from multiprocessing import Queue
import sys

class LoggingService():
    """
    Intializes a thread that listens on a queue to log messages to a file or stderr.

    :param log_file: Path to the file we should log to.
    :type log_file: str

    :param stderr: Should the log be logged to stderr?
    :type stderr: bool
    """
    LOG_FORMAT_BRIEF = "%(levelname)s :: %(msg)s"

    def __init__(self, log_file, stderr):
        self.queue = Queue()

        if stderr:
            handler = logging.StreamHandler(sys.stderr)
        else:
            handler = logging.FileHandler(log_file)

        formatter = logging.Formatter(self.LOG_FORMAT_BRIEF)
        handler.setFormatter(formatter)
        self._queuelistener = logging.handlers.QueueListener(self.queue, handler)

    def start(self):
        """
        Start the logging service thread.
        """
        self._queuelistener.start()

def service_configure_logging(queue):
    """
    Configure the current root logger to send log records to a queue.
    Note the root logger stays the same after you fork, this should be used only once.
    Otherwise logs will get repeated.

    :param queue: The queue to send logs to.
    :type queue: :class:`Queue`
    """
    handler = logging.handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
