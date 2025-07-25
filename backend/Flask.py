from flask import Flask, render_template, request, jsonify import csv import io import os import time

app = Flask(name)

Mock product database

products = [ {"id": "001", "name": "Milk", "price": 50.0}, {"id": "002", "name": "Bread", "price": 30.0}, {"id": "003", "name": "Eggs", "price": 15.0}, {"id": "004", "name": "Soda", "price": 10.0}, {"id": "005", "name":"maize flour", "price ]

transactions = [] transaction_id_counter = 1

Admin credentials (use environment variables in production)

ADMIN_USER = os.environ.get('ADMIN_USER', "admin") ADMIN_PASS = os.environ.get('ADMIN_PASS', "StarSon2025")

@app.route('/') def index(): return render_template('index.html')

@app.route('/admin_login', methods=['POST']) def admin_login(): data = request.get_json() username = data.get('username') password = data.get('password')

if username == ADMIN_USER and password == ADMIN_PASS:
    return jsonify({'success': True})
else:
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/products') def get_products(): return jsonify(products)

@app.route('/generate_receipt', methods=['POST']) def generate_receipt(): global transaction_id_counter data = request.get_json()

payment_method = data.get('paymentMethod', 'Cash')
cart_items = data.get('items', [])

total = sum(item['price'] * item['qty'] for item in cart_items)

new_transaction = {
    'id': transaction_id_counter,
    'payment_method': payment_method,
    'items': cart_items,
    'total': total,
    'status': 'processing'
}
transactions.append(new_transaction)
transaction_id_counter += 1

return jsonify({
    'receipt_id': new_transaction['id'],
    'payment_method': payment_method,
    'total': total,
    'items': cart_items,
    'qr_img': f'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=StarSon_Receipt_{new_transaction["id"]}'
})

@app.route('/initiate_mpesa', methods=['POST']) def initiate_mpesa(): data = request.get_json() phone = data.get('phone') amount = data.get('amount') # TODO: Integrate with Safaricom Daraja API here return jsonify({'success': True, 'message': f'STK push sent to {phone} for KES {amount}'})

@app.route('/initiate_airtel', methods=['POST']) def initiate_airtel(): data = request.get_json() phone = data.get('phone') amount = data.get('amount') # TODO: Integrate with Airtel Money API here return jsonify({'success': True, 'message': f'Airtel money request sent to {phone} for KES {amount}'})

@app.route('/initiate_card', methods=['POST']) def initiate_card(): data = request.get_json() amount = data.get('amount') # Simulate card processing time.sleep(3) return jsonify({'success': True, 'message': f'Card payment of KES {amount} successful'})
@app.route('/initiate_cash', methods=['POST']) def initiate_card(): data = request.get_json() amount = data.get('amount') # Simulate card processing time.sleep(3) return jsonify({'success': True, 'message': f'Cash payment of KES {amount} successful'})

@app.route('/onboard_sms_gateway', methods=['POST']) def onboard_sms_gateway(): data = request.get_json() provider_name = data.get('provider') gateway_url = data.get('url') api_key = data.get('api_key') # Save or validate credentials return jsonify({'success': True, 'message': f'SMS gateway {provider_name} onboarded successfully.'})

@app.route('/onboard_mobile_money', methods=['POST']) def onboard_mobile_money(): data = request.get_json() provider_name = data.get('provider') credentials = data.get('credentials') # Save or validate credentials return jsonify({'success': True, 'message': f'Mobile Money provider {provider_name} onboarded successfully.'})

@app.route('/export_inventory') def export_inventory(): csv_buffer = io.StringIO() writer = csv.writer(csv_buffer) writer.writerow(['Product ID', 'Name', 'Price']) for product in products: writer.writerow([product['id'], product['name'], product['price']])

return csv_buffer.getvalue(), 200, {
    'Content-Type': 'text/csv',
    'Content-Disposition': 'attachment; filename=inventory.csv'
}

if name == 'main': app.run(debug=True)
