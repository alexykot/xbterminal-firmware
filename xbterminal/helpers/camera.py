import logging
import time
import threading

import cv2
from PIL import Image

from xbterminal.helpers import qr

logger = logging.getLogger(__name__)


class Worker(threading.Thread):

    fps = 2

    def __init__(self, camera):
        super(Worker, self).__init__()
        self.camera = camera
        self.data = None
        self._stop = threading.Event()

    def run(self):
        logger.debug('qr scanner started')
        while True:
            if self._stop.is_set():
                break
            retcode, data = self.camera.read()
            time.sleep(1 / self.fps)
            if not retcode or not data.any():
                logger.error('could not get image from camera')
                break
            image = Image.fromarray(data[..., ::-1])  # Convert from BGR to RGB
            data = qr.decode(image)
            if data:
                logger.debug('qr scanner has decoded message: {0}'.format(data))
                self.data = data
        logger.debug('qr scanner stopped')

    def stop(self):
        self._stop.set()


class QRScanner(object):

    def __init__(self, source=0):
        self._camera = cv2.VideoCapture(source)
        if not self.is_available():
            logger.warning('camera is not available')
        else:
            logger.info('camera is active')
        self.worker = None

    def is_available(self):
        return self._camera is not None and self._camera.isOpened()

    def start(self):
        if self.is_available() and not self.worker:
            self.worker = Worker(self._camera)
            self.worker.start()

    def stop(self):
        if self.worker and self.worker.is_alive():
            self.worker.stop()
            self.worker.join()
        self.worker = None

    def get_data(self):
        if self.worker is not None:
            return self.worker.data
