import os
import time
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from graph import build_graph
from gmail_client import get_flow, exchange_code_for_token
from database import db

SHARED_SECRET = os.getenv("SHARED_SECRET", "")

# CORS configuration
ALLOWED_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000").split(",")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS]

app = FastAPI(title="Parently Backend", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
_last_run = 0
COOLDOWN_SECONDS = int(os.getenv("RUN_COOLDOWN_SECONDS", "30"))

graph = build_graph()

def check_auth(x_api_key: str | None):
    if SHARED_SECRET and x_api_key != SHARED_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/health")
def health():
    return {"ok": True, "service": "parently-backend"}

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/run-digest")
def run_digest(x_api_key: str | None = Header(default=None)):
    check_auth(x_api_key)
    
    # Rate limiting
    global _last_run
    now = time.time()
    if now - _last_run < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - _last_run))
        raise HTTPException(
            status_code=429, 
            detail=f"Please wait {remaining} seconds before running again."
        )
    _last_run = now
    
    try:
        result = graph.invoke({
            "pdf_folder": os.getenv("PDF_FOLDER","./sample-data/pdfs"),
            "reminders_path": os.getenv("REMINDERS_PATH","./sample-data/reminders.json"),
            "gmail_json": os.getenv("GMAIL_JSON","./sample-data/gmail.json"),
            "gmail_query": os.getenv("GMAIL_QUERY","newer_than:7d label:School"),
        })
        
        # Save items and digest to database
        items = result.get("items", [])
        if items:
            db.save_items(items)
        
        digest_md = result.get("digest_md", "")
        if digest_md:
            from datetime import date
            db.save_digest(date.today(), digest_md)
        
        return {
            "ok": True,
            "digest_md": digest_md,
            "items": items,
            "output_path": result.get("output_path")
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "hint": "Check logs for details"
        }

@app.get("/digest/today")
def digest_today(x_api_key: str | None = Header(default=None)):
    check_auth(x_api_key)
    from datetime import date
    
    # Try database first
    digest_md = db.get_digest(date.today())
    if digest_md:
        return {"ok": True, "markdown": digest_md}
    
    # Fallback to file system
    path = f"./out/digest_{date.today().isoformat()}.md"
    if not os.path.exists(path):
        return {"ok": False, "message": "No digest yet"}
    return {"ok": True, "markdown": open(path, encoding="utf-8").read()}

# --- Gmail OAuth flow ---
@app.get("/auth/google/start")
def auth_google_start(request: Request):
    base = os.getenv("BACKEND_PUBLIC_URL") or str(request.base_url).rstrip("/")
    redirect_uri = f"{base}/auth/google/callback"
    try:
        flow = get_flow(redirect_uri)
        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent")
        return RedirectResponse(url=auth_url)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/auth/google/callback")
def auth_google_callback(code: str = "", request: Request = None):
    base = os.getenv("BACKEND_PUBLIC_URL") or (str(request.base_url).rstrip("/") if request else "")
    redirect_uri = f"{base}/auth/google/callback"
    try:
        res = exchange_code_for_token(code, redirect_uri)
        return JSONResponse({"ok": True, "message": "Gmail authorized. You can run the digest now."})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
