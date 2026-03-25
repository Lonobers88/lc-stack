# Open WebUI Config

Automatisch gegenereerd door `scripts/export_openwebui_config.py`.

## Workspace Models
- `arena-model`
- `bge-m3:latest`
- `nomic-embed-text:latest`
- `qwen3.5:9b`
- `qwen3:14b`
- `redux-hr-assistent`
- `redux-medewerker`
- `redux-prijszoeker`

## Structuur
- `models/` — Model definities (system prompt, tools, knowledge)
- `tools/` — Tool Python code + metadata
- `filters/` — Filter/Function Python code + metadata
- `knowledge_index.json` — Overzicht van knowledge collections (docs zitten in vector DB)

## Restore
Om config te restoren, gebruik de Open WebUI API of importeer handmatig via de UI.
Een restore script volgt nog.
