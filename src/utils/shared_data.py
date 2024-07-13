import json


def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


json_data = None


def initialize_data(file_path):
    global json_data
    json_data = load_json_data(file_path)


def get_json_data():
    global json_data
    if json_data is None:
        raise ValueError("JSON data not initialized. Call initialize_data() first.")
    return json_data
