import requests

def send_custom_sms(config, number, message):
    try:
        payload_template = config["payload_template"]
        payload = {k: v.replace("{number}", number).replace("{message}", message) 
                   for k, v in payload_template.items()}
        response = requests.request(
            method=config.get("method", "POST"),
            url=config["url"],
            headers=config.get("headers", {}),
            json=payload
        )
        return response.json()
    except Exception as e:
        return {"status": "failed", "error": str(e)}
