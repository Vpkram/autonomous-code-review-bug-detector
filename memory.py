import json
import os
import datetime

MEMORY_FILE = "fixes_memory.json"

# Saves a bug description and its corresponding fix code to memory.
def save_fix(bug_description: str, fix_code: str):
    """
    Saves a resolved bug description and its fix code into a local JSON database
    with a timestamp. Creates the file if it does not exist.
    """
    try:
        data = {}
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}

        data[bug_description] = {
            "fix": fix_code,
            "timestamp": datetime.datetime.now().isoformat()
        }

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"Memory: Saved fix for bug description: '{bug_description}'")
    except Exception as e:
        print(f"Memory Error: Failed to save fix: {e}")


# Recalls a stored fix code if a similar bug description is found.
def recall_similar_fix(bug_description: str) -> str or None:
    """
    Checks if a similar bug has been fixed previously by comparing word overlaps.
    Returns the stored fix code if at least 3 matching words are found.
    """
    try:
        if not os.path.exists(MEMORY_FILE):
            return None

        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        input_words = set(bug_description.lower().split())

        for stored_desc, info in data.items():
            stored_words = set(stored_desc.lower().split())
            matching_words = len(input_words.intersection(stored_words))
            if matching_words >= 3:
                print(f"Memory: Recalled similar fix for '{stored_desc}' (matching words: {matching_words})")
                return info.get("fix")

        return None
    except Exception as e:
        print(f"Memory Error: Failed to recall fix: {e}")
        return None
