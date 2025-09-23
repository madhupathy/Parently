import os, json
from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def _cred_paths():
    # Credentials are read-only (Secret Files on Render)
    cred_dir = os.getenv("GMAIL_CRED_DIR", "./secrets")
    # Tokens are writable (use DATA_DIR on Render)
    data_dir = os.getenv("DATA_DIR", "./data")
    os.makedirs(data_dir, exist_ok=True)
    return (
        os.path.join(cred_dir, "credentials.json"),
        os.path.join(data_dir, "token.json")
    )

def get_flow(redirect_uri: str) -> Flow:
    cred_path, _ = _cred_paths()
    if not os.path.exists(cred_path):
        raise FileNotFoundError("Missing credentials.json. Place it in GMAIL_CRED_DIR or ./secrets")
    flow = Flow.from_client_secrets_file(cred_path, scopes=SCOPES)
    flow.redirect_uri = redirect_uri
    return flow

def exchange_code_for_token(code: str, redirect_uri: str) -> Dict[str, Any]:
    flow = get_flow(redirect_uri)
    flow.fetch_token(code=code)
    creds = flow.credentials
    _, token_path = _cred_paths()
    with open(token_path, "w") as f:
        f.write(creds.to_json())
    return {"ok": True}

def get_creds() -> Optional[Credentials]:
    cred_path, token_path = _cred_paths()
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return creds

def gmail_service() -> Any:
    creds = get_creds()
    if not creds:
        raise RuntimeError("Gmail not authorized yet. Visit /auth/google/start to authorize.")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)

def list_messages(query: str, max_results: int = 20) -> List[Dict[str, Any]]:
    svc = gmail_service()
    user_id = "me"
    resp = svc.users().messages().list(userId=user_id, q=query, maxResults=max_results).execute()
    ids = [m["id"] for m in resp.get("messages", [])]
    out = []
    for mid in ids:
        msg = svc.users().messages().get(userId=user_id, id=mid, format="full").execute()
        out.append(parse_message(msg))
    return out

def _get_header(payload_headers, name: str) -> str:
    for h in payload_headers:
        if h.get("name","").lower() == name.lower():
            return h.get("value","")
    return ""

def parse_message(msg) -> Dict[str, Any]:
    headers = msg.get("payload", {}).get("headers", [])
    subject = _get_header(headers, "Subject")
    sender = _get_header(headers, "From")
    date = _get_header(headers, "Date")
    # Decode body text
    body_text = ""
    def walk_parts(p):
        nonlocal body_text
        if p is None: return
        if "data" in (p.get("body") or {}):
            import base64
            try:
                data = base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8", errors="ignore")
                body_text += "\n" + data
            except Exception:
                pass
        for part in p.get("parts",[]) or []:
            walk_parts(part)
    walk_parts(msg.get("payload"))
    return {
        "id": msg.get("id"),
        "date": date,
        "from": sender,
        "subject": subject,
        "text": body_text.strip(),
        "attachments": []
    }
