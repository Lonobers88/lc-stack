# Open WebUI Microsoft 365 Mail Integration (Scaffold)

Minimal FastAPI service to connect Microsoft 365 mailboxes via delegated OAuth and expose read-only email operations for Open WebUI tools.

## Features
- Delegated OAuth (admin connects mailbox via browser consent)
- SQLite storage for mailbox tokens (`data/`)
- Read-only message listing + per-message summarization scaffolding
- Draft reply suggestions (plain JSON text only; no Graph drafts created)

## Endpoints
- `GET /health`
- `GET /auth/start`
- `GET /auth/callback`
- `GET /mailboxes`
- `GET /messages?mailbox_id=...&top=...&folder=...`
- `POST /summarize_message`
- `POST /draft_reply`

## Environment Variables
Required:
- `M365_CLIENT_ID`
- `M365_CLIENT_SECRET`
- `M365_REDIRECT_URI`

Optional:
- `M365_TENANT_ID` (default: `common`)
- `M365_SCOPES` (default: `offline_access https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/User.Read`)
- `M365_DB_PATH` (default: `data/mailboxes.sqlite3`)
- `GRAPH_BASE_URL` (default: `https://graph.microsoft.com/v1.0`)

If you decide to call the optional Graph draft helper, add `https://graph.microsoft.com/Mail.ReadWrite` to `M365_SCOPES`.

## Local Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export M365_CLIENT_ID=...
export M365_CLIENT_SECRET=...
export M365_REDIRECT_URI=http://localhost:8000/auth/callback
# Optional
export M365_TENANT_ID=common

uvicorn app.main:app --reload
```

Open the consent flow:
```
http://localhost:8000/auth/start
```

## Docker
```bash
docker build -t m365-mail-service .
docker run --rm -p 8000:8000 \
  -e M365_CLIENT_ID=... \
  -e M365_CLIENT_SECRET=... \
  -e M365_REDIRECT_URI=http://localhost:8000/auth/callback \
  m365-mail-service
```

Or using compose:
```bash
docker compose up --build
```

## Open WebUI Tool
See `tools/openwebui_tool_m365.py` for callable tool functions:
- `create_connection_link`
- `list_mailboxes`
- `list_messages`
- `summarize_message`
- `draft_reply`

## Notes
- This scaffold intentionally keeps message processing lightweight.
- Draft replies are suggestions only. No email is sent or drafted in Microsoft 365 by the API.
