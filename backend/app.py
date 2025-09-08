import os
from flask import Flask, render_template, request, jsonify, send_file
from flask_mail import Mail, Message
from twilio.rest import Client
from dotenv import load_dotenv
import io
import csv
import qrcode
from eco_receipt import generate_pdf_receipt, get_tree_saving_stats

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Config for Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.zoho.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'info@brightarm.co.ke')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
mail = Mail(app)

# Config for Twilio
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Admin credentials
ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
ADMIN_PASS = os.getenv('ADMIN_PASS', 'StarSon2025')

# Mock DB
products = [
    {"id": "001", "name": "Milk", "price": 50.0},
    {"id": "002", "name": "Bread", "price": 30.0},
    {"id": "003", "name": "Eggs", "price": 15.0},
    {"id": "004", "name": "Soda", "price": 10.0}
]
transactions = []
transaction_id_counter = 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data.get('username') == ADMIN_USER and data.get('password') == ADMIN_PASS:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/products')
def get_products():
    return jsonify(products)

@app.route('/generate_receipt', methods=['POST'])
def generate_receipt():
    global transaction_id_counter
    try:
        data = request.get_json()
        items = data.get('items', [])
        payment_method = data.get('paymentMethod', 'Cash')
        phone = data.get('phone')
        email = data.get('email')

        total = sum(item['price'] * item['qty'] for item in items)
        receipt_id = transaction_id_counter
        customer_number = f"Customer-{receipt_id}"
        transaction_id_counter += 1

        # Tree-saving stats
        stats = get_tree_saving_stats(items)

        # Generate PDF (pass customer_number)
        pdf_buffer = generate_pdf_receipt(receipt_id, items, total, stats, customer_number=customer_number)

        # Save transaction
        transactions.append({
            'id': receipt_id,
            'items': items,
            'total': total,
            'method': payment_method,
            'customer_number': customer_number
        })

        # QR code
        qr_img_url = f'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=StarSon_Receipt_{receipt_id}'

        # Send email
        if email:
            msg = Message("Your StarSon Receipt", recipients=[email])
            msg.body = f"Thank you for shopping, {customer_number}. Total: {total}. Tree saving: {stats}"
            msg.attach(f"receipt_{receipt_id}.pdf", "application/pdf", pdf_buffer.getvalue())
            mail.send(msg)

        # Send SMS
        if phone:
            sms_msg = f"StarSon Receipt #{receipt_id} for {customer_number}. Total: {total}. Tree saving: {stats}"
            twilio_client.messages.create(
                body=sms_msg,
                from_=TWILIO_PHONE_NUMBER,
                to=phone
            )

        return jsonify({
            'receipt_id': receipt_id,
            'total': total,
            'tree_stats': stats,
            'qr_img': qr_img_url,
            'customer_number': customer_number
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export_inventory')
def export_inventory():
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['Product ID', 'Name', 'Price'])
    for p in products:
        writer.writerow([p['id'], p['name'], p['price']])
    return buffer.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=inventory.csv'
    }

@app.route('/download_pdf/<int:receipt_id>')
def download_pdf(receipt_id):
    transaction = next((t for t in transactions if t['id'] == receipt_id), None)
    if not transaction:
        return 'Not found', 404

    stats = get_tree_saving_stats(transaction['items'])
    customer_number = transaction.get('customer_number', f"Customer-{receipt_id}")
    pdf_buffer = generate_pdf_receipt(receipt_id, transaction['items'], transaction['total'], stats, customer_number=customer_number)
    return send_file(io.BytesIO(pdf_buffer.getvalue()),
                     download_name=f"receipt_{receipt_id}.pdf",
                     as_attachment=True,
                     mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
