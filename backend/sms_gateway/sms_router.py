from sms_gateway.config_loader import load_sms_config
from sms_gateway.android_gateway import send_android_sms
from sms_gateway.branded_gateway import send_branded_sms
from sms_gateway.custom_gateway import send_custom_sms

def send_sms(client_id, number, message):
    config = load_sms_config(client_id)
    mode = config.get("mode")

    if mode == "android":
        return send_android_sms(config["device_url"], number, message)

    elif mode == "branded":
        return send_branded_sms(config, number, message)

    elif mode == "custom":
        return send_custom_sms(config, number, message)

    else:
        return {"status": "error", "message": "SMS mode not configured"}
      
