import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .config import get_settings


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_conn() -> sqlite3.Connection:
    settings = get_settings()
    os.makedirs(os.path.dirname(settings.database_path), exist_ok=True)
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS mailboxes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            display_name TEXT,
            tenant_id TEXT,
            token_json TEXT NOT NULL DEFAULT '{}',
            provider TEXT NOT NULL DEFAULT 'm365',
            imap_config TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS oauth_states (
            state TEXT PRIMARY KEY,
            created_at TEXT NOT NULL
        )
        """
    )
    # Migratie: voeg kolommen toe aan bestaande tabel indien niet aanwezig
    existing = [row[1] for row in cur.execute("PRAGMA table_info(mailboxes)").fetchall()]
    if "provider" not in existing:
        cur.execute("ALTER TABLE mailboxes ADD COLUMN provider TEXT NOT NULL DEFAULT 'm365'")
    if "imap_config" not in existing:
        cur.execute("ALTER TABLE mailboxes ADD COLUMN imap_config TEXT")
    conn.commit()
    conn.close()


def insert_oauth_state(state: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO oauth_states (state, created_at) VALUES (?, ?)",
        (state, _utc_now()),
    )
    conn.commit()
    conn.close()


def pop_oauth_state(state: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT state FROM oauth_states WHERE state = ?", (state,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False
    cur.execute("DELETE FROM oauth_states WHERE state = ?", (state,))
    conn.commit()
    conn.close()
    return True


def upsert_mailbox(
    email: str,
    display_name: Optional[str],
    tenant_id: Optional[str],
    token: Dict[str, Any],
) -> int:
    conn = get_conn()
    cur = conn.cursor()
    now = _utc_now()
    token_json = json.dumps(token)
    cur.execute("SELECT id FROM mailboxes WHERE email = ?", (email,))
    row = cur.fetchone()
    if row:
        mailbox_id = row["id"]
        cur.execute(
            """
            UPDATE mailboxes
            SET display_name = ?, tenant_id = ?, token_json = ?, updated_at = ?
            WHERE id = ?
            """,
            (display_name, tenant_id, token_json, now, mailbox_id),
        )
    else:
        cur.execute(
            """
            INSERT INTO mailboxes (email, display_name, tenant_id, token_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (email, display_name, tenant_id, token_json, now, now),
        )
        mailbox_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(mailbox_id)


def get_mailbox(mailbox_id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM mailboxes WHERE id = ?", (mailbox_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def update_mailbox_token(mailbox_id: int, token: Dict[str, Any]) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE mailboxes SET token_json = ?, updated_at = ? WHERE id = ?",
        (json.dumps(token), _utc_now(), mailbox_id),
    )
    conn.commit()
    conn.close()


def load_mailbox_token(mailbox: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(mailbox["token_json"])


def upsert_google_workspace_mailbox(
    email: str,
    display_name: Optional[str],
    service_account_json: str,
) -> int:
    """Sla een Google Workspace mailbox op met service account credentials."""
    conn = get_conn()
    cur = conn.cursor()
    now = _utc_now()
    # imap_config hergebruiken voor google service account JSON
    cur.execute("SELECT id FROM mailboxes WHERE email = ?", (email,))
    row = cur.fetchone()
    if row:
        mailbox_id = row["id"]
        cur.execute(
            """
            UPDATE mailboxes
            SET display_name = ?, provider = 'google', imap_config = ?, token_json = '{}', updated_at = ?
            WHERE id = ?
            """,
            (display_name, service_account_json, now, mailbox_id),
        )
    else:
        cur.execute(
            """
            INSERT INTO mailboxes (email, display_name, tenant_id, token_json, provider, imap_config, created_at, updated_at)
            VALUES (?, ?, NULL, '{}', 'google', ?, ?, ?)
            """,
            (email, display_name, service_account_json, now, now),
        )
        mailbox_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(mailbox_id)


def upsert_imap_mailbox(
    email: str,
    display_name: Optional[str],
    imap_host: str,
    imap_port: int,
    imap_ssl: bool,
    username: str,
    password: str,
) -> int:
    conn = get_conn()
    cur = conn.cursor()
    now = _utc_now()
    imap_config = json.dumps({
        "imap_host": imap_host,
        "imap_port": imap_port,
        "imap_ssl": imap_ssl,
        "username": username,
        "password": password,
    })
    cur.execute("SELECT id FROM mailboxes WHERE email = ?", (email,))
    row = cur.fetchone()
    if row:
        mailbox_id = row["id"]
        cur.execute(
            """
            UPDATE mailboxes
            SET display_name = ?, provider = 'imap', imap_config = ?, token_json = '{}', updated_at = ?
            WHERE id = ?
            """,
            (display_name, imap_config, now, mailbox_id),
        )
    else:
        cur.execute(
            """
            INSERT INTO mailboxes (email, display_name, tenant_id, token_json, provider, imap_config, created_at, updated_at)
            VALUES (?, ?, NULL, '{}', 'imap', ?, ?, ?)
            """,
            (email, display_name, imap_config, now, now),
        )
        mailbox_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(mailbox_id)


def list_mailboxes() -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, email, display_name, tenant_id, provider, created_at, updated_at FROM mailboxes ORDER BY id DESC"
    )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def upsert_google_oauth_mailbox(
    db_path: str,
    email: str,
    display_name: Optional[str],
    tokens: str,
) -> int:
    """Sla een Google OAuth mailbox op met OAuth tokens (token_json kolom)."""
    import sqlite3, datetime
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    now = datetime.datetime.utcnow().isoformat() + "Z"
    cur = c.cursor()
    cur.execute("SELECT id FROM mailboxes WHERE email = ?", (email,))
    row = cur.fetchone()
    if row:
        mailbox_id = row["id"]
        cur.execute(
            "UPDATE mailboxes SET display_name=?, provider='google', token_json=?, updated_at=? WHERE id=?",
            (display_name, tokens, now, mailbox_id),
        )
    else:
        cur.execute(
            "INSERT INTO mailboxes (email, display_name, tenant_id, token_json, provider, imap_config, created_at, updated_at) VALUES (?, ?, NULL, ?, 'google', NULL, ?, ?)",
            (email, display_name, tokens, now, now),
        )
        mailbox_id = cur.lastrowid
    c.commit()
    c.close()
    return int(mailbox_id)

