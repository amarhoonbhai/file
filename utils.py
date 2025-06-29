import json
import os

DATA_FILE = "bot_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": [], "files_shared": 0}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def add_user(user_id):
    data = load_data()
    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_data(data)

def increment_files_shared():
    data = load_data()
    data["files_shared"] += 1
    save_data(data)

def get_stats():
    data = load_data()
    return len(data["users"]), data["files_shared"]
