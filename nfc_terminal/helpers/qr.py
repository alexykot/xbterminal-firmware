import os
import qrcode


def qr_gen(uri):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image()
    return img


def current_dir():
    dir = os.getcwd() + "/"
    return dir


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

'''
# Set filename for qr image, and ensure directory exists
filename = current_dir() + "/img/" + "qrcode.png"
ensure_dir(filename)

qr_gen().save(filename)
'''