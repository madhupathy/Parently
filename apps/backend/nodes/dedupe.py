def dedupe_items(state):
    seen, deduped = set(), []
    for it in state.get("items", []):
        key = (it.get("subject","").strip().lower(), (it.get("text","")[:120]).strip().lower())
        if key not in seen:
            seen.add(key)
            deduped.append(it)
    state["items"] = deduped
    return state
