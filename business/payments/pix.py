import qrcode
from uuid import uuid4

class Pix:
    def __init__(self):
        pass

    def create_payment(self):
        
        bank_payment_id = uuid4()
        hash_payment = f'qr_code_payment_{bank_payment_id}'

        img = qrcode.make(hash_payment)
        img.save(f'static/img/qr_code_payment_{bank_payment_id}.png')
        
        return {
            'bank_payment_id': str(bank_payment_id),
            'qrcode_path': hash_payment
        }