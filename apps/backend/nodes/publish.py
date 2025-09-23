import os
from datetime import date

def publish_digest(state):
    os.makedirs("./out", exist_ok=True)
    path = f"./out/digest_{date.today().isoformat()}.md"
    with open(path,"w",encoding="utf-8") as f:
        f.write(state.get("digest_md",""))
    state["output_path"] = path
    return state
