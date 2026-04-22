# LocalCompute AI Stack (`lc-stack`)

Deployable stack for a **LocalCompute AI** appliance — a self-hosted, GPU-backed
AI workspace designed to run on a single NVIDIA box (RTX 4090 / 5090 class)
on Ubuntu 22.04 / 24.04 LTS.

Tied together in one `docker compose` file, seeded with a curated set of
OpenWebUI models, tools and filters, and fronted by a Cloudflare tunnel.

## What it ships

Container services (see `docker-compose.yml`):

| Service | Role |
|---|---|
| `ollama` | Local LLM runtime (model catalog seeded via `install/seed_owui.py`) |
| `openwebui` | Primary UI — chat, RAG, tools, filters |
| `qdrant` | Vector store for RAG / knowledge bases |
| `whisper` | Speech-to-text |
| `searxng` | Privacy-friendly search for web-grounded tools |
| `m365-mail-service` | Microsoft 365 mailbox OAuth + mail ingest |
| `cloudflared` | Fixed Cloudflare tunnel for external access |

Top-level layout:

| Path | What |
|---|---|
| `install.sh` | Fresh-install script (Ubuntu + NVIDIA + Docker + stack) |
| `update.sh` | Client-safe update with backup & rollback |
| `healthcheck.sh` | Stack-wide health probe |
| `docker-compose.yml` | All services + networking |
| `.env.example` | Env template (M365 and other secrets) |
| `install/` | OpenWebUI seed (`owui_seed.json`) + seeder (`seed_owui.py`) |
| `patches/` | In-tree patches applied on top of upstream OpenWebUI (`env.py`, `middleware.py`, `retrieval_utils.py`) |
| `scripts/` | Operational scripts (daily briefing, config export, reset-to-master) |
| `openwebui-config/` | OpenWebUI runtime config overlays |
| `searxng/` | SearXNG config |
| `m365-mail-service/` | Source of the M365 mail sidecar |
| `docs/DEPLOYMENT.md` | Full deployment guide (Dutch) |

## Quick start

```bash
git clone https://github.com/Lonobers88/lc-stack.git
cd lc-stack
cp .env.example .env   # fill in M365 + any other secrets
sudo bash install.sh
```

See `docs/DEPLOYMENT.md` for the full guide including hardware minima,
NVIDIA driver setup, and first-boot tasks.

## Latest summary

**2026-04-18** — recent focus has been client-ready (`klant`) configuration:
deterministic behavior via enabled API keys + disabled persistent config,
neutral system prompts that don't leak Redux / Qwen branding, health
monitoring + deployment documentation, an `update.sh` with backup and
rollback, and a RAG grounding filter (`lc_rag_grounding`) for the knowledge
base.

Earlier in April the stack was tightened into a two-model "klant install"
surface (AI Assistent + Setup Assistent), reworked around `gemma4:26b` and
`qwen3.5:35b` defaults, and had Google Workspace OAuth 2.0 + a fixed
Cloudflare tunnel added. A full `redux-*` → `lc-*` ID rename (models,
tools, filters) went through at the start of the month.

See `CHANGELOG.md` for the grouped history.

## Status

This is not a generic public product. It's the deployable form of
LocalCompute's appliance and is versioned as needed. No semver promise; see
commit history and `CHANGELOG.md`.
