import json
import os

CONFIG_PATH = "last_session.json"

DEFAULT_CONFIG = {
    "machine_type": "",
    "fault_status": "",
    "rotation_speed": "",
    "rotor_configuration": "",
    "mic_position": "",
    "session_name": ""
}

def load_last_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return {**DEFAULT_CONFIG, **config}
    return DEFAULT_CONFIG

def save_last_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)
