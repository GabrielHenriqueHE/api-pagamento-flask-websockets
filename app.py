from flask import Flask, jsonify, request, send_file, render_template
from datetime import datetime, timedelta

from business.payments.pix import Pix
from models.payment import Payment
from repository.database import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'SECRET_KEY_WEBSOCKET'


db.init_app(app)

@app.route('/payments/pix', methods=['POST'])
def create_payment_pix():

    data = request.json

    if 'value' not in data:
        return jsonify({
            'message': 'Invalid value.'
        }), 400
    
    expiration_date = datetime.now() + timedelta(minutes=30)
    
    payment = Payment(value=data.get('value'), expiration_date=expiration_date)

    pix = Pix()
    pix_payment_data = pix.create_payment()
    payment.bank_payment_id = pix_payment_data['bank_payment_id']
    payment.qrcode = pix_payment_data['qrcode_path']

    db.session.add(payment)
    db.session.commit()

    return jsonify({
        'message': 'The payment has been created.',
        'payment': payment.to_dict()
    })

@app.route('/payments/pix/qrcode/<file_name>', methods=['GET'])
def get_pix_image(file_name):
    return send_file(f'static/img/{file_name}.png', mimetype='image/png')

@app.route('/payments/pix/confirmation', methods=['POST'])
def pix_payment_confirmation():
    return jsonify({
        'message': 'The payment has been confirmed.'
    })

@app.route('/payments/pix/<int:payment_id>', methods=['GET'])
def payment_pix_page(payment_id):
    payment = Payment.query.get(payment_id)

    return render_template('payment.html', payment_id=payment.id, payment_value=payment.value, host='http://localhost:5000', qrcode=payment.qrcode)

if __name__ == '__main__':
    app.run(debug=True)
