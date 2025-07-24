import requests
from requests.auth import HTTPBasicAuth
from flask import Flask, request, jsonify
import datetime
import base64

app = Flask(__name__)

# Replace with your own details
CONSUMER_KEY = 'your_consumer_key'
CONSUMER_SECRET = 'your_consumer_secret'
SHORTCODE = '174379'  # Test shortcode or live one
PASSKEY = 'your_passkey'
CALLBACK_URL = 'https://yourdomain.com/callback'

def get_access_token():
    response = requests.get(
        'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
        auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET)
    )
    return response.json().get('access_token')

def lipa_na_mpesa(phone_number, amount, account_ref):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((SHORTCODE + PASSKEY + timestamp).encode()).decode()
    token = get_access_token()

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": "StarSon POS Payment"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
        json=payload,
        headers=headers
    )
    return response.json()

@app.route('/initiate_payment', methods=['POST'])
def initiate_payment():
    data = request.json
    return lipa_na_mpesa(data['phone'], data['amount'], data['account_ref'])

if __name__ == '__main__':
    app.run(debug=True)
