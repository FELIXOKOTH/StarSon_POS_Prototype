
# sms_gateway/branded_gateway.py

import requests
from requests.auth import HTTPBasicAuth

def send_branded_sms(provider, config, recipient, message):
    if provider == 'safaricom':
        return send_via_safaricom(config, recipient, message)
    elif provider == 'airtel':
        return send_via_airtel(config, recipient, message)
    else:
        return {"status": "error", "message": f"Unsupported provider: {provider}"}


# --- Safaricom Branded SMS Integration ---
def send_via_safaricom(config, recipient, message):
    token = get_safaricom_token(config['consumer_key'], config['consumer_secret'])
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "recipient": recipient,
        "sender_id": config.get("sender_id"),
        "message": message
    }

    # Replace with actual endpoint when provided
    url = config.get("sms_endpoint")
    response = requests.post(url, json=payload, headers=headers)

    return {
        "status": response.status_code,
        "response": response.text
    }


def get_safaricom_token(consumer_key, consumer_secret):
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Token generation failed: {response.text}")


# --- Airtel Branded SMS Integration ---
def send_via_airtel(config, recipient, message):
    url = config.get("sms_endpoint")
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": config.get("api_key")
    }

    payload = {
        "sender": config.get("sender_id"),
        "to": recipient,
        "message": message
    }

    response = requests.post(url, json=payload, headers=headers)

    return {
        "status": response.status_code,
        "response": response.text
    }
