import json
from datetime import datetime
from pathlib import Path

STATUS_FILE = Path("chapter_status.json")

# Default structure
def load_status():
    if not STATUS_FILE.exists():
        return {}
    with open(STATUS_FILE, "r") as f:
        return json.load(f)

def save_status(status_data):
    with open(STATUS_FILE, "w") as f:
        json.dump(status_data, f, indent=2)

def update_status(chapter_id, stage, metadata=None):
    status = load_status()
    chapter_status = status.get(chapter_id, {})
    chapter_status["status"] = stage
    chapter_status["updated_at"] = datetime.now().isoformat()
    if metadata:
        chapter_status.update(metadata)
    status[chapter_id] = chapter_status
    save_status(status)
    print(f"📌 {chapter_id} marked as '{stage}'")

def get_status(chapter_id):
    return load_status().get(chapter_id)

def get_all_statuses():
    return load_status()
