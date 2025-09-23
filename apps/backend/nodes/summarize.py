import os

def _openai_summarize(body: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    SYS = "Create a concise parent digest for TODAY. Group by child if possible. Order: Actions due today/tomorrow, Reminders, Info. Bullet points, include dates."
    resp = client.responses.create(
        model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),
        input=[{"role":"system","content":SYS},{"role":"user","content":body}],
        temperature=0.2
    )
    return resp.output_text

def _ollama_summarize(body: str) -> str:
    import requests
    SYS = "Create a concise parent digest for TODAY. Group by child if possible. Order: Actions due today/tomorrow, Reminders, Info. Bullet points, include dates."
    prompt = SYS + "\n\n" + body
    try:
        resp = requests.post("http://localhost:11434/api/generate", json={"model":"llama3.1", "prompt": prompt, "stream": False}, timeout=30)
        if resp.ok:
            return resp.json().get("response","")
    except Exception:
        pass
    return body

def summarize_digest(state):
    bullets = "\n".join([
        f"- [{', '.join(it.get('tags',[]))}] {it.get('title','')} — {it.get('subject','')}"
        for it in state.get("items", [])
    ])
    if os.getenv("USE_OLLAMA","").lower() == "true":
        md = _ollama_summarize(bullets)
    else:
        try:
            md = _openai_summarize(bullets)
        except Exception:
            md = bullets
    state["digest"] = md
    state["digest_md"] = f"# What parents need to know today\n\n{md}"
    return state
