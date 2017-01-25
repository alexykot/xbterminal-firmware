import logging
import os
import time
import threading
import subprocess

from PIL import Image

from xbterminal.rpc.utils import qr
from xbterminal.rpc.settings import RUNTIME_PATH

logger = logging.getLogger(__name__)


class FsWebCamBackend(object):

    fps = 30

    def __init__(self):
        self.image_path = os.path.join(RUNTIME_PATH, 'camera.jpg')
        self.device = None
        for idx in range(5):
            path = '/dev/video{}'.format(idx)
            if self._check_device(path):
                self.device = path
                if idx == 0:
                    self.resolution = '480x320'
                else:
                    self.resolution = '640x480'
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

    def stop(self):
        self._stop.set()


class QRScanner(object):

    backends = {
        'fswebcam': FsWebCamBackend,
    }

    def __init__(self, backend='fswebcam'):
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
            logger.debug('qr scanner started')

    def stop(self):
        if self.worker and self.worker.is_alive():
            self.worker.stop()
            self.worker.join()
            logger.debug('qr scanner stopped')
        self.worker = None

    def get_data(self):
        if self.worker is not None:
            return self.worker.data
