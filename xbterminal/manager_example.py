"""
Usage:
import xbterminal.manager
manager = xbterminal.manager.XBTerminalManager()
manager.start()
"""
import logging
import threading
import time

from xbterminal import stages_example

logger = logging.getLogger(__name__)


class XBTerminalManager(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.period = 0.1
        self.stage = "init"

    def run(self):
        logger.info("manager started")
        while True:
            next_stage = getattr(stages_example, self.stage)()
            if next_stage is not None:
                self.stage = next_stage
            else:
                # Stage remains the same
                time.sleep(self.period)



