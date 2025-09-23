import os, json, requests

SYS = """You are a parent assistant. Given a school message, return strict JSON:
{"title":"...","tags":["Action:...","Reminder:...","Info:..."],"due_date": "YYYY-MM-DD or null","who":"child/grade or null"}
Top-level tags must be one of: Action, Reminder, Info. Be concise."""

def _ollama_generate(prompt: str, model: str = "llama3.1") -> str:
    try:
        import requests
        resp = requests.post("http://localhost:11434/api/generate", json={"model": model, "prompt": prompt, "stream": False}, timeout=30)
        if resp.ok:
            data = resp.json()
            return data.get("response","").strip()
    except Exception:
        pass
    return ""

def _openai_generate(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    resp = client.responses.create(
        model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),
        input=[{"role":"system","content":SYS},{"role":"user","content":prompt}],
        temperature=0.2
    )
    return resp.output_text.strip()

def classify_one(text: str):
    prompt = f"Message:\n{text}\nReturn JSON only."
    out = ""
    if os.getenv("USE_OLLAMA","").lower() == "true":
        out = _ollama_generate(SYS + "\n\n" + prompt)
    else:
        try:
            out = _openai_generate(prompt)
        except Exception:
            out = ""
    try:
        return json.loads(out)
    except Exception:
        return {"title":"Untitled","tags":["Info"],"due_date":None,"who":None}

def classify_and_tag(state):
    enriched = []
    for it in state.get("items", []):
        meta = classify_one((it.get("text") or "")[:4000])
        it.update(meta)
        enriched.append(it)
    state["items"] = enriched
    return state
