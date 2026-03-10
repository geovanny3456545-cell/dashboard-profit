import json
import os
import datetime

NOTES_FILE = "calendar_notes.json"

def load_notes():
    """Loads notes from the JSON file."""
    if not os.path.exists(NOTES_FILE):
        return {}
    
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading notes: {e}")
        return {}

def save_notes(notes):
    """Saves notes to the JSON file."""
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving notes: {e}")

def get_note_for_date(date_obj):
    """Returns the note text for a specific datetime.date object."""
    notes = load_notes()
    key = date_obj.isoformat()
    return notes.get(key, "")

def save_note_for_date(date_obj, text):
    """Updates the note for a specific date."""
    notes = load_notes()
    key = date_obj.isoformat()
    
    if text.strip():
        notes[key] = text.strip()
    else:
        # Remove empty notes
        if key in notes:
            del notes[key]
            
    save_notes(notes)
