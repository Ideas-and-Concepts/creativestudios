import json
import os

DB_FILE = "creativestudios_db.json"

def load_memory():
    """Load the app database from JSON file."""
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_memory(database: dict):
    """Save the app database to JSON file."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=4)