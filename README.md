# Parently — parent’s desk in your pocket

Parently is an Agentic AI that scans school communications (emails, PDFs, reminders) and produces a **daily digest** for parents, tagging items as **Action**, **Reminder**, or **Info**.

**Stack**: LangGraph + FastAPI (Render) · Next.js (Vercel) · OpenAI (or Ollama)

## Quick start
- Backend (Render): FastAPI endpoints `/run-digest`, `/digest/today`, `/auth/google/*`
- Frontend (Vercel): Next.js App Router with proxy API and Markdown rendering
