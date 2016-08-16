import logging
import threading

from PyQt4 import QtCore

from xbterminal.gui import stages

logger = logging.getLogger(__name__)


class SignalProxy(QtCore.QObject):

    signal = QtCore.pyqtSignal(str, tuple)

    def _emit(self, *args):
        self.signal.emit(self.method_name, args)

    def __getattr__(self, attr):
        self.method_name = attr
        return self._emit


class StageWorker(QtCore.QObject):

    finished = QtCore.pyqtSignal()

    def __init__(self, current_stage, runtime):
        super(StageWorker, self).__init__()
        self.current_stage = current_stage
        self.next_stage = None
        self.runtime = runtime
        self.ui = SignalProxy()

    def run(self):
        logger.debug("moving to stage {0}".format(self.current_stage))
        func = getattr(stages, self.current_stage)
        self.next_stage = func(self.runtime, self.ui)
        self.finished.emit()


class StageWorkerThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(StageWorkerThread, self).__init__(*args, **kwargs)
        self.daemon = True


def move_to_thread(worker):
    """
    Run StageWorker inside the python thread
    """
    thread = StageWorkerThread(target=worker.run)
    thread.start()
    return thread
