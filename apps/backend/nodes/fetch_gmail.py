import os, json
from typing import Dict, Any
from gmail_client import list_messages

def fetch_gmail(state: Dict[str, Any]) -> Dict[str, Any]:
    query = state.get("gmail_query") or os.getenv("GMAIL_QUERY","newer_than:7d label:School")
    try:
        messages = list_messages(query=query, max_results=int(os.getenv("GMAIL_MAX_RESULTS","20")))
    except Exception:
        # Fallback to sample data if live fetch fails
        path = state.get("gmail_json", "./sample-data/gmail.json")
        try:
            with open(path, encoding="utf-8") as f:
                messages = json.load(f)
        except Exception:
            messages = []
    state["gmail_messages"] = messages
    return state
