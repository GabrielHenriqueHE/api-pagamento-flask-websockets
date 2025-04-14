import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from business.payments.pix import Pix

def test_pix_create_payment():
    pix = Pix()

    payment_info = pix.create_payment()

    assert 'bank_payment_id' in payment_info
    assert 'qrcode_path' in payment_info

    qrcode_path = payment_info['qrcode_path']

    assert os.path.isfile(f'static/img/{qrcode_path}.png')