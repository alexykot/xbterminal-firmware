import logging
import time

import cv2
from PIL import Image

from xbterminal.helpers import qr

logger = logging.getLogger(__name__)


class Camera(object):

    def __init__(self, source=0):
        self._camera = cv2.VideoCapture(source)
        if not self.is_active():
            logger.warning('camera is not available')
        else:
            logger.info('camera is active')

    def is_active(self):
        return self._camera is not None and self._camera.isOpened()

    def get_image(self):
        retcode, data = self._camera.read()
        time.sleep(1)
        if not retcode:
            return None
        image = Image.fromarray(data[..., ::-1])  # Convert from BGR to RGB
        logger.debug('read image from camera ({0}x{1})'.format(*image.size))
        return image

    def decode_qr(self):
        image = self.get_image()
        if image:
            return qr.decode(image)
