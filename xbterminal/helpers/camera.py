import logging
import os
import time
import threading
import subprocess

from PIL import Image
try:
    import cv2
except ImportError:
    pass

from xbterminal.helpers import qr
from xbterminal.defaults import RUNTIME_PATH

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


class FsWebCamBackend(object):

    fps = 30
    resolution = '640x480'

    def __init__(self):
        self.image_path = os.path.join(RUNTIME_PATH, 'camera.jpg')
        self.device = None
        for idx in range(5):
            path = '/dev/video{}'.format(idx)
            if self._check_device(path):
                self.device = path
                logger.info('camera found at {}'.format(self.device))
                break

    def _check_device(self, path):
        try:
            output = subprocess.check_output(
                ['fswebcam', '--device', path],
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            return False
        else:
            return 'Captured frame' in output

    def is_available(self):
        if self.device:
            return self._check_device(self.device)
        else:
            return False

    def get_image(self):
        """
        Returns PIL.Image instance or None
        """
        try:
            output = subprocess.check_output([
                'fswebcam',
                '--device', self.device,
                '--resolution', self.resolution,
                '--fps', str(self.fps),
                '--skip', '1',
                '--no-banner',
                self.image_path,
            ], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            logger.exception(error)
            return None
        if 'Writing JPEG image' not in output:
            return None
        image = Image.open(self.image_path)
        return image


class Worker(threading.Thread):

    fps = 2

    def __init__(self, camera):
        super(Worker, self).__init__()
        self.daemon = True
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
        'fswebcam': FsWebCamBackend,
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
