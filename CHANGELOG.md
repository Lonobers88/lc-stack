# Changelog

Grouped from commit history. This project doesn't promise semver; entries
are organized by date / theme from the actual commits.

The only semi-formal release tag in history is `v1.0.0-prototype`
(2026-04-02). Everything since has been incremental hardening for client
(`klant`) installs.

## 2026-04-18 — Client determinism + RAG grounding

- Enable API keys and disable persistent config so client deployments behave
  deterministically (`5711116`).

## 2026-04-12 — Ops

- Stack-wide health monitoring + deployment documentation (`56261d2`).

## 2026-04-11 — Update path + RAG

- `update.sh` for client stack updates, with backup and rollback (`dcdbe48`).
- `lc_rag_grounding` filter code added for the RAG knowledge base (`747496e`).
- Default model flipped to `gemma4:26b` with client-neutral system prompts
  (`e73d05a`).

## 2026-04-03 — Client-neutral two-model surface

- Client-neutral system prompt for "AI Assistent" (no Redux / Qwen
  references) (`45d5827`).
- Reduced model catalog to **AI Assistent + Setup Assistent** for client
  installs (`d0e376c`).
- All LC models aligned on `qwen3.5:35b` as default (`c9240e1`).
- Misc fixes: interne tekst verwijderd uit LC Kennisbank Zoeker omschrijving
  (`34f48c1`); seeder schema fix for OWUI latest + removed
  `lc_pc_prijszoeker` from seed (`15a2948`).

## 2026-04-02 — Google Workspace + rename + v1.0.0-prototype

- Google Workspace OAuth 2.0 koppeling (`69d6cee`), with follow-up fix for
  redirect URI trailing slash (`a42b198`) and seed entries for Google OAuth
  setup tool functions (`86050b0`).
- Repo-wide rename of `redux-*` IDs → `lc-*` across models, tools, and
  filters (`9271b37`).
- Setup Assistent v2.0.0 (`7592fe2`).
- Tag `v1.0.0-prototype` cut (`2a7a134`).
- Exact Online integration: add account-name lookup via `crm/Accounts`,
  clean invoice output, pipe filter for OWUI (`d400108`).

## 2026-03-26 — Exact Online + Cloudflare tunnel

- Fixed Cloudflare tunnel added to `docker-compose` (`9c261c8`).
- Exact Online API response parsing + date formatting fixes (`120ffdd`).
- Initial Exact Online koppeling successfully tested + bugfix for
  `expires_in` type cast (`012d664`).

---

Older history: see `git log` for any entries before 2026-03-26.
