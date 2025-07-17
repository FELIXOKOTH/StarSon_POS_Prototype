from flask import Flask, render_template, request, jsonify, abort
import csv
import io
import os
import secrets
from functools import wraps
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

# === Mock Databases ===
products = [
    {"id": "001", "name": "Milk", "price": 50.0},
    {"id": "002", "name": "Bread", "price": 30.0},
    {"id": "003", "name": "Eggs", "price": 15.0},
    {"id": "004", "name": "Soda", "price": 10.0}
]

transactions = []
transaction_id_counter = 1
TOKENS = set()

# === Admin Credentials (Prototype Only) ===
ADMIN_USER = os.environ.get('ADMIN_USER', "admin")
ADMIN_PASS = os.environ.get('ADMIN_PASS', "StarSon2025")

# === Token Decorator ===
def require_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token not in TOKENS:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

# === Routes ===

@app.route('/')
def index():
    return render_template('index.html')  # Make sure templates/index.html exists

@app.route('/admin_login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if username == ADMIN_USER and password == ADMIN_PASS:
            token = secrets.token_hex(16)
            TOKENS.add(token)
            return jsonify({'success': True, 'token': token})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/products')
@require_token
def get_products():
    return jsonify(products)

@app.route('/generate_receipt', methods=['POST'])
@require_token
def generate_receipt():
    global transaction_id_counter
    try:
        data = request.get_json()
        payment_method = data.get('paymentMethod')
        cart_items = data.get('items')

        if not payment_method or not isinstance(cart_items, list):
            raise BadRequest("Invalid or missing payment method/items")

        for item in cart_items:
            if not all(k in item for k in ['id', 'name', 'price', 'qty']):
                raise BadRequest("Each cart item must have id, name, price, qty")

        total = sum(item['price'] * item['qty'] for item in cart_items)

        new_transaction = {
            'id': transaction_id_counter,
            'payment_method': payment_method,
            'items': cart_items,
            'total': total
        }
        transactions.append(new_transaction)
        transaction_id_counter += 1

        qr_url = f'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=StarSon_Receipt_{new_transaction["id"]}'

        return jsonify({
            'receipt_id': new_transaction['id'],
            'payment_method': payment_method,
            'total': total,
            'items': cart_items,
            'qr_img': qr_url
        })

    except BadRequest as br:
        return jsonify({'error': str(br)}), 400
    except Exception as e:
        return jsonify({'error': f'Receipt generation failed: {str(e)}'}), 500

@app.route('/export_inventory')
@require_token
def export_inventory():
    try:
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(['Product ID', 'Name', 'Price'])
        for product in products:
            writer.writerow([product['id'], product['name'], product['price']])
        return csv_buffer.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=inventory.csv'
        }
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

# === Run App ===
if __name__ == '__main__':
    app.run(debug=True)
