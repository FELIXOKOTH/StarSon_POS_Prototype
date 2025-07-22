import requests

def send_android_sms(device_url, number, message):
    try:
        payload = {
            "phone": number,
            "message": message
        }
        response = requests.post(device_url, json=payload, timeout=5)
        return response.json()
    except Exception as e:
        return {"status": "failed", "error": str(e)}
