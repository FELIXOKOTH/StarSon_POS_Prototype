import json

def load_sms_config(client_id):
    with open("client_configs.json", "r") as f:
        configs = json.load(f)
    return configs.get(client_id, {})
