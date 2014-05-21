"""
Usage:
import xbterminal.manager
manager = xbterminal.manager.XBTerminalManager()
manager.start()
"""
import logging
import threading
import time

from xbterminal import stages_

logger = logging.getLogger(__name__)


class XBTerminalManager(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.period = 0.1
        self.stage = None

    def run(self):
        logger.info("manager started")
        while True:
            if self.stage is not None:
                self.stage = getattr(stages, self.stage)()
            time.sleep(self.period)



