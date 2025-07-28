import requests

def send_android_sms(device_url, number, message):
    try:
        payload = {
            "phone": number,
            "message": message
        }
        response = requests.post(device_url, json=payload, timeout=5)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {"status": "failed", "error": f"HTTP error: {http_err}"}
    except requests.exceptions.ConnectionError:
        return {"status": "failed", "error": "Connection error"}
    except requests.exceptions.Timeout:
        return {"status": "failed", "error": "Request timed out"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
