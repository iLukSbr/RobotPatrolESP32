import json

class JSONParser:
    def __init__(self):
        self.json_message = {}

    def print_json(self):
        print(self.json_message)

    def add_data(self, key, value):
        keys = key.split('.')
        d = self.json_message
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    def get_json_message(self):
        try:
            message = json.dumps(self.json_message)
            return message
        except Exception as e:
            print(f"Failed to create JSON message: {e}")
            return None
        
    def clear_json_message(self):
        self.json_message = {}
        