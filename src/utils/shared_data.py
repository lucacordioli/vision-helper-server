import json

json_data = None


def initialize_data(_json_data: str):
    global json_data
    json_data = json.loads(_json_data)


def get_json_data():
    global json_data
    if json_data is None:
        raise ValueError("JSON data not initialized. Call initialize_data() first.")
    return json_data
