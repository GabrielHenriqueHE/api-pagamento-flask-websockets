from flask import Flask, jsonify, request, send_file, render_template
from flask_socketio import SocketIO
from datetime import datetime, timedelta

from business.payments.pix import Pix
from models.payment import Payment
from repository.database import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'SECRET_KEY_WEBSOCKET'


db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins='http://127.0.0.1:5000')

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
    data = request.get_json()

    if 'bank_payment_id' not in data and 'value' not in data:
        return jsonify({
            'message': 'Invalid payment data.'
        }), 400

    payment = Payment.query.filter_by(bank_payment_id=data.get('bank_payment_id')).first()

    if not payment or payment.paid == True:
        return jsonify({
            'message': 'Payment not found'
        }), 404
    
    if data.get('value') != payment.value:
        return jsonify({
            'message':'Invalid payment data.'
        }), 400
    
    payment.paid = True
    db.session.commit()

    socketio.emit(f'payment-confirmed-{payment.id}')

    return jsonify({
        'message': 'The payment has been confirmed.'
    })

@app.route('/payments/pix/<int:payment_id>', methods=['GET'])
def payment_pix_page(payment_id):
    payment = Payment.query.get(payment_id)
    
    if not payment:
        return render_template('404.html')

    if payment.paid:
        return render_template('confirmed_payment.html', qrcode=payment.qrcode, payment_id=payment.id, payment_value=payment.value)

    return render_template('payment.html', payment_id=payment.id, payment_value=payment.value, host='http://localhost:5000', qrcode=payment.qrcode)

@socketio.on('connect')
def handle_connect():
    print('Client connected.')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected.')

if __name__ == '__main__':
    socketio.run(app, debug=True)
