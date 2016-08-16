import zbar


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
