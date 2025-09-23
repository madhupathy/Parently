import json, csv, os

def read_reminders(state):
    path = state.get("reminders_path", "./sample-data/reminders.json")
    items = []
    if os.path.exists(path):
        try:
            if path.endswith(".json"):
                items = json.load(open(path, encoding="utf-8"))
            elif path.endswith(".csv"):
                with open(path, encoding="utf-8") as f:
                    items = list(csv.DictReader(f))
        except Exception:
            items = []
    state["reminder_items"] = items
    return state
