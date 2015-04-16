import os

import qrcode
import zbar
from PIL import Image


def qr_gen(content, path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=1,
    )
    qr.add_data(content)
    qr.make(fit=True)

    img = qr.make_image()
    img.save(path)


def decode(image):
    """
    Code taken from qrtools (https://launchpad.net/qr-tools)
    """
    # Configure the reader
    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
    # Obtain image data
    width, height = image.size
    raw = image.convert('L').tostring()  # black and white
    # Scan the image
    wrapper = zbar.Image(width, height, 'Y800', raw)
    result = scanner.scan(wrapper)
    if result == 0:
        return None
    else:
        for symbol in wrapper:
            pass
        del wrapper
        return symbol.data.decode('utf-8')
