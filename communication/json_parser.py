import json

class JSONParser:
    def __init__(self):
        self.json_message = {}

    def print_json(self):
        print(self.json_message)

    def add_data(self, key, value):
        self.json_message[key] = value

    def get_json_message(self):
        try:
            message = json.dumps(self.json_message)
            self.json_message = {}
            return message
        except Exception as e:
            print(f"Failed to create JSON message: {e}")
            return None