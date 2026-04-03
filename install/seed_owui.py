#!/usr/bin/env python3
"""
seed_owui.py - Importeer LocalCompute OWUI configuratie in een verse installatie.

Gebruik:
  docker exec openwebui python3 /app/install/seed_owui.py

Of vanuit de host:
  docker cp install/seed_owui.py openwebui:/tmp/seed_owui.py
  docker cp install/owui_seed.json openwebui:/tmp/owui_seed.json
  docker exec openwebui python3 /tmp/seed_owui.py
"""

import sqlite3
import json
import time
import os
import sys

SEED_FILE = os.path.join(os.path.dirname(__file__), "owui_seed.json")
if not os.path.exists(SEED_FILE):
    SEED_FILE = "/tmp/owui_seed.json"

DB = "/app/backend/data/webui.db"


def get_admin_user_id(cur):
    """Haal de eerste admin user op."""
    row = cur.execute(
        "SELECT id FROM user WHERE role='admin' ORDER BY created_at ASC LIMIT 1"
    ).fetchone()
    if not row:
        raise ValueError("Geen admin user gevonden. Maak eerst een admin account aan via de OWUI UI.")
    return row[0]


def seed_tools(cur, tools, user_id, now):
    inserted = 0
    skipped = 0
    for tool in tools:
        existing = cur.execute("SELECT id FROM tool WHERE id=?", (tool["id"],)).fetchone()
        if existing:
            skipped += 1
            continue
        cur.execute(
            """INSERT INTO tool (id, user_id, name, content, specs, meta, valves, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                tool["id"],
                user_id,
                tool["name"],
                tool["content"],
                json.dumps(tool.get("specs", []), ensure_ascii=False),
                json.dumps(tool.get("meta", {}), ensure_ascii=False),
                "{}",
                now,
                now,
            ),
        )
        inserted += 1
    return inserted, skipped


def seed_functions(cur, functions, user_id, now):
    inserted = 0
    skipped = 0
    for fn in functions:
        existing = cur.execute("SELECT id FROM function WHERE id=?", (fn["id"],)).fetchone()
        if existing:
            skipped += 1
            continue
        cur.execute(
            """INSERT INTO function (id, user_id, name, type, content, meta, is_active, is_global, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                fn["id"],
                user_id,
                fn["name"],
                fn["type"],
                fn["content"],
                json.dumps(fn.get("meta", {}), ensure_ascii=False),
                1,
                0,
                now,
                now,
            ),
        )
        inserted += 1
    return inserted, skipped


def seed_models(cur, models, user_id, now):
    inserted = 0
    skipped = 0
    for model in models:
        existing = cur.execute("SELECT id FROM model WHERE id=?", (model["id"],)).fetchone()
        if existing:
            skipped += 1
            continue
        cur.execute(
            """INSERT INTO model (id, user_id, base_model_id, name, params, meta, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                model["id"],
                user_id,
                model.get("base_model_id", ""),
                model["name"],
                json.dumps(model.get("params", {}), ensure_ascii=False),
                json.dumps(model.get("meta", {}), ensure_ascii=False),
                now,
                now,
            ),
        )
        inserted += 1
    return inserted, skipped


def main():
    print(f"LocalCompute OWUI Seed v1.0")
    print(f"DB: {DB}")
    print(f"Seed: {SEED_FILE}")
    print()

    if not os.path.exists(SEED_FILE):
        print(f"ERROR: Seed bestand niet gevonden: {SEED_FILE}")
        sys.exit(1)

    with open(SEED_FILE) as f:
        seed = json.load(f)

    print(f"Seed versie: {seed.get('version', 'onbekend')}")
    print(f"  {len(seed.get('tools', []))} tools")
    print(f"  {len(seed.get('functions', []))} filters/functions")
    print(f"  {len(seed.get('models', []))} workspace modellen")
    print()

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = int(time.time())

    try:
        user_id = get_admin_user_id(cur)
        print(f"Admin user: {user_id}")
    except ValueError as e:
        print(f"ERROR: {e}")
        conn.close()
        sys.exit(1)

    # Seed tools
    ins, skip = seed_tools(cur, seed.get("tools", []), user_id, now)
    print(f"Tools: {ins} ingevoegd, {skip} overgeslagen (bestonden al)")

    # Seed functions/filters
    ins, skip = seed_functions(cur, seed.get("functions", []), user_id, now)
    print(f"Filters: {ins} ingevoegd, {skip} overgeslagen")

    # Seed models
    ins, skip = seed_models(cur, seed.get("models", []), user_id, now)
    print(f"Modellen: {ins} ingevoegd, {skip} overgeslagen")

    conn.commit()
    conn.close()

    print()
    print("✅ Seed compleet. Herstart Open WebUI:")
    print("   docker restart openwebui")


if __name__ == "__main__":
    main()
