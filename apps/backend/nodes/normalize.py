from datetime import datetime

def normalize_items(state):
    out = []
    for m in state.get("gmail_messages", []):
        out.append({
            "id": m.get("id"),
            "source": "gmail",
            "date": m.get("date") or datetime.utcnow().isoformat(),
            "from": m.get("from"),
            "subject": m.get("subject"),
            "text": m.get("text",""),
            "attachments": m.get("attachments",[])
        })
    for p in state.get("pdf_items", []):
        p = dict(p)
        p["id"] = p.get("subject")
        p["date"] = p.get("date") or datetime.utcnow().isoformat()
        out.append(p)
    for r in state.get("reminder_items", []):
        out.append({
            "id": r.get("id") or r.get("title"),
            "source": "reminder",
            "date": r.get("date") or datetime.utcnow().isoformat(),
            "from": r.get("from",""),
            "subject": r.get("title","Reminder"),
            "text": r.get("text","")
        })
    state["items"] = out
    return state
