import logging
import threading

from PyQt4 import QtCore

logger = logging.getLogger(__name__)

from xbterminal.stages import stages


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


def move_to_thread(worker):
    """
    Run StageWorker inside the python thread
    """
    thread = threading.Thread(target=worker.run)
    thread.start()
    return thread


def move_to_qthread(worker):
    """
    Run StageWorker inside the QThread
    """
    thread = QtCore.QThread()
    worker.moveToThread(thread)
    worker.finished.connect(thread.quit)
    thread.started.connect(worker.run)
    thread.start()
    return thread
