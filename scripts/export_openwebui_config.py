#!/usr/bin/env python3
"""
export_openwebui_config.py
Exporteert alle Open WebUI workspace config naar openwebui-config/
voor versiebeheer in git.

Gebruik: python3 scripts/export_openwebui_config.py
"""

import json
import os
import sys
import subprocess
import requests
from pathlib import Path

OWUI_URL = os.getenv("OWUI_URL", "http://localhost:3000")
OWUI_EMAIL = os.getenv("OWUI_EMAIL", "elonclawd@gmail.com")
OWUI_PASSWORD = os.getenv("OWUI_PASSWORD", "BotDicksforDinner55!")
OUTPUT_DIR = Path(__file__).parent.parent / "openwebui-config"


def get_token():
    resp = requests.post(
        f"{OWUI_URL}/api/v1/auths/signin",
        json={"email": OWUI_EMAIL, "password": OWUI_PASSWORD},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["token"]


def export_models(headers):
    resp = requests.get(f"{OWUI_URL}/api/v1/models?base=false", headers=headers)
    resp.raise_for_status()
    models = resp.json().get("data", [])

    out_dir = OUTPUT_DIR / "models"
    out_dir.mkdir(parents=True, exist_ok=True)

    exported = []
    for m in models:
        mid = m.get("id", "")
        info = m.get("info", {})
        if not info:
            continue  # Skip base Ollama models

        # Sla alleen workspace models op (die een info dict hebben)
        model_export = {
            "id": mid,
            "name": info.get("name"),
            "base_model_id": info.get("base_model_id"),
            "meta": info.get("meta", {}),
            "is_active": info.get("is_active", True),
        }

        filename = out_dir / f"{mid}.json"
        filename.write_text(json.dumps(model_export, indent=2, ensure_ascii=False))
        exported.append(mid)
        print(f"  ✓ Model: {mid}")

    return exported


def export_tools(headers):
    resp = requests.get(f"{OWUI_URL}/api/v1/tools/", headers=headers)
    resp.raise_for_status()
    tools = resp.json()

    out_dir = OUTPUT_DIR / "tools"
    out_dir.mkdir(parents=True, exist_ok=True)

    for tool in tools:
        tid = tool.get("id", "")
        tool_export = {
            "id": tid,
            "name": tool.get("name"),
            "meta": tool.get("meta", {}),
            "content": tool.get("content", ""),
        }

        # Sla Python code ook apart op voor leesbaarheid
        py_file = out_dir / f"{tid}.py"
        py_file.write_text(tool.get("content", ""))

        # Sla metadata op als JSON
        meta_file = out_dir / f"{tid}.meta.json"
        meta_export = {k: v for k, v in tool_export.items() if k != "content"}
        meta_file.write_text(json.dumps(meta_export, indent=2, ensure_ascii=False))

        print(f"  ✓ Tool: {tid}")


def export_filters(headers):
    resp = requests.get(f"{OWUI_URL}/api/v1/functions/", headers=headers)
    resp.raise_for_status()
    functions = resp.json()

    out_dir = OUTPUT_DIR / "filters"
    out_dir.mkdir(parents=True, exist_ok=True)

    for fn in functions:
        fid = fn.get("id", "")
        fn_export = {
            "id": fid,
            "name": fn.get("name"),
            "type": fn.get("type"),
            "meta": fn.get("meta", {}),
            "content": fn.get("content", ""),
        }

        py_file = out_dir / f"{fid}.py"
        py_file.write_text(fn.get("content", ""))

        meta_file = out_dir / f"{fid}.meta.json"
        meta_export = {k: v for k, v in fn_export.items() if k != "content"}
        meta_file.write_text(json.dumps(meta_export, indent=2, ensure_ascii=False))

        print(f"  ✓ Filter/Function: {fid}")


def export_knowledge_index(headers):
    resp = requests.get(f"{OWUI_URL}/api/v1/knowledge/", headers=headers)
    resp.raise_for_status()
    data = resp.json()
    collections = data.get("items", []) if isinstance(data, dict) else data

    out_dir = OUTPUT_DIR
    index = []
    for c in collections:
        index.append({
            "id": c.get("id"),
            "name": c.get("name"),
            "description": c.get("description"),
        })

    (out_dir / "knowledge_index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False)
    )
    print(f"  ✓ Knowledge index ({len(index)} collections)")


def write_readme(models_exported):
    readme = f"""# Open WebUI Config

Automatisch gegenereerd door `scripts/export_openwebui_config.py`.

## Workspace Models
{chr(10).join(f'- `{m}`' for m in sorted(models_exported))}

## Structuur
- `models/` — Model definities (system prompt, tools, knowledge)
- `tools/` — Tool Python code + metadata
- `filters/` — Filter/Function Python code + metadata
- `knowledge_index.json` — Overzicht van knowledge collections (docs zitten in vector DB)

## Restore
Om config te restoren, gebruik de Open WebUI API of importeer handmatig via de UI.
Een restore script volgt nog.
"""
    (OUTPUT_DIR / "README.md").write_text(readme)
    print("  ✓ README.md")


def main():
    print("🔄 Open WebUI config exporteren...")
    print(f"   URL: {OWUI_URL}")

    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    print("\n📦 Models:")
    models = export_models(headers)

    print("\n🔧 Tools:")
    export_tools(headers)

    print("\n⚙️  Filters/Functions:")
    export_filters(headers)

    print("\n📚 Knowledge:")
    export_knowledge_index(headers)

    write_readme(models)

    print(f"\n✅ Export klaar → {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
