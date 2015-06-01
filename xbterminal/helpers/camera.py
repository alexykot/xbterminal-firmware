import logging
import time
import threading

import cv2
from PIL import Image

from xbterminal.helpers import qr

logger = logging.getLogger(__name__)


class OpenCVBackend(object):

    source_index = 0

    def __init__(self):
        self._camera = cv2.VideoCapture(self.source_index)

    def is_available(self):
        return self._camera is not None and self._camera.isOpened()

    def get_image(self):
        """
        Should return PIL Image instance or None
        """
        retcode, data = self._camera.read()
        if not retcode or not data.any():
            return None
        image = Image.fromarray(data[..., ::-1])  # Convert from BGR to RGB
        return image


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
            image = self.camera.get_image()
            time.sleep(1 / self.fps)
            if not image:
                logger.error('could not get image from camera')
                break
            data = qr.decode(image)
            if data:
                logger.debug('qr scanner has decoded message: {0}'.format(data))
                self.data = data
        logger.debug('qr scanner stopped')

    def stop(self):
        self._stop.set()


class QRScanner(object):

    backends = {
        'opencv': OpenCVBackend,
    }

    def __init__(self, backend='opencv'):
        logger.info('using {0} backend'.format(backend))
        self.camera = self.backends[backend]()
        if not self.camera.is_available():
            logger.warning('camera is not available')
        else:
            logger.info('camera is active')
        self.worker = None

    def start(self):
        if self.camera.is_available() and not self.worker:
            self.worker = Worker(self.camera)
            self.worker.start()

    def stop(self):
        if self.worker and self.worker.is_alive():
            self.worker.stop()
            self.worker.join()
        self.worker = None

    def get_data(self):
        if self.worker is not None:
            return self.worker.data
