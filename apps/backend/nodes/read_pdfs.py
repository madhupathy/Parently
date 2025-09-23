import os
from pypdf import PdfReader

def read_pdfs(state):
    folder = state.get("pdf_folder", "./sample-data/pdfs")
    items = []
    if os.path.isdir(folder):
        for name in os.listdir(folder):
            if name.lower().endswith(".pdf"):
                path = os.path.join(folder, name)
                try:
                    text = "\n".join([p.extract_text() or "" for p in PdfReader(path).pages])
                except Exception:
                    text = ""
                items.append({
                    "source": "pdf",
                    "subject": name,
                    "text": text,
                    "attachments": [path]
                })
    state["pdf_items"] = items
    return state
