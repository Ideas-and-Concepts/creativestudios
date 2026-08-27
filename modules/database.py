import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "creativestudios_db.json")

def load_memory() -> dict:
    """Load the Creative Studios database from JSON file."""
    if not os.path.exists(DB_FILE):
        return {"projects": []}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"projects": []}

def save_memory(database: dict) -> None:
    """Save the Creative Studios database back to JSON file."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2)