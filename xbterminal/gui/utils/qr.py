import qrcode


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
