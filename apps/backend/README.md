# Parently Backend (FastAPI + LangGraph)

Endpoints:
- GET /health
- POST /run-digest
- GET /digest/today
- GET /auth/google/start
- GET /auth/google/callback

Auth: send `x-api-key: SHARED_SECRET`.

Local dev:
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
export SHARED_SECRET=devkey
uvicorn app:app --reload
```

Gmail OAuth (Live Ingestion):
1) Create OAuth client in Google Cloud Console.
2) Place `credentials.json` at `./secrets/credentials.json` (or set `GMAIL_CRED_DIR`).
3) Set `BACKEND_PUBLIC_URL` to your Render URL.
4) Visit `/auth/google/start` and approve.
5) Set `GMAIL_QUERY`, e.g. `newer_than:7d label:School`.
