#!/bin/bash
# ============================================================
# reset_to_master.sh — LocalCompute AI Stack
# Bereidt het systeem voor als MASTER SSD (out-of-box)
# Wist alle klantdata maar behoudt software, modellen en config
#
# GEBRUIK: sudo bash reset_to_master.sh
# WAARSCHUWING: ONHERROEPELIJK — maak eerst een backup
# ============================================================

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${YELLOW}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║   LocalCompute MASTER RESET — Out-of-Box voorbereiding ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "${RED}WAARSCHUWING: Dit wist alle gebruikersdata, chats, mailboxen en accounts.${NC}"
echo -e "${RED}Software, AI-modellen en systeemconfiguratie blijven behouden.${NC}"
echo ""
read -p "Weet je het zeker? Typ 'MASTER' om door te gaan: " confirm
if [ "$confirm" != "MASTER" ]; then
    echo "Afgebroken."
    exit 0
fi

echo ""
echo "▶ Stap 1: Backup maken van huidige data..."
BACKUP_DIR="$HOME/backups/pre-reset-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
docker run --rm \
    -v openwebui:/data \
    -v "$BACKUP_DIR":/backup \
    ubuntu tar czf /backup/openwebui-data.tar.gz /data 2>/dev/null && \
    echo "  ✓ OWUI backup: $BACKUP_DIR/openwebui-data.tar.gz" || \
    echo "  ⚠ OWUI backup mislukt (geen data?)"

cp ~/lc-stack/m365-mail-service/data/mailboxes.sqlite3 "$BACKUP_DIR/mailboxes.sqlite3" 2>/dev/null && \
    echo "  ✓ Mailbox backup opgeslagen" || \
    echo "  ⚠ Geen mailbox database gevonden"

echo ""
echo "▶ Stap 2: Containers stoppen..."
cd ~/lc-stack
docker compose stop openwebui m365-mail-service

echo ""
echo "▶ Stap 3: OWUI gebruikersdata wissen..."
# Wis specifieke tabellen via Python script in container
docker start openwebui 2>/dev/null || true
sleep 3
docker exec openwebui python3 - << 'PYEOF'
import sqlite3, os

db_path = '/app/backend/data/webui.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Tabellen met klantdata — wissen
WIPE_TABLES = [
    'user', 'auth',           # Gebruikersaccounts
    'chat', 'chat_message',   # Chatgeschiedenis
    'chatidtag', 'tag',       # Chat tags
    'message', 'message_reaction',  # Berichten
    'memory',                 # Geheugen/notities
    'feedback',               # Feedback
    'folder',                 # Mappen
    'api_key',                # API sleutels
    'oauth_session',          # OAuth sessies
    'note',                   # Notities
    'prompt_history',         # Prompt geschiedenis
    'file', 'chat_file',      # Geüploade bestanden
    'channel', 'channel_member', 'channel_webhook', 'channel_file',  # Kanalen
    'group', 'group_member',  # Groepen
    'access_grant',           # Toegangsrechten
]

# Tabellen BEWAREN (systeem/config)
KEEP_TABLES = [
    'config',           # Systeemconfiguratie
    'model',            # Workspace modellen (redux-medewerker etc.)
    'tool',             # Tools
    'function',         # Filters/pipes
    'knowledge',        # Kennisbank-definities (niet de inhoud)
    'knowledge_file',   # Kennisbank bestandskoppelingen
    'prompt',           # Opgeslagen prompts
    'skill',            # Skills
    'alembic_version',  # DB versie
    'migratehistory',   # Migratie history
    'document',         # Document metadata
]

wiped = []
errors = []
for table in WIPE_TABLES:
    try:
        count = cur.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        cur.execute(f'DELETE FROM {table}')
        wiped.append(f'{table} ({count} rijen)')
    except Exception as e:
        errors.append(f'{table}: {e}')

conn.commit()

# Vacuum om ruimte vrij te maken
cur.execute('VACUUM')
conn.close()

print('✓ Gewiste tabellen:')
for t in wiped:
    print(f'  - {t}')
if errors:
    print('⚠ Fouten:')
    for e in errors:
        print(f'  - {e}')
PYEOF

echo ""
echo "▶ Stap 4: Mailbox database wissen..."
rm -f ~/lc-stack/m365-mail-service/data/mailboxes.sqlite3
echo "  ✓ Mailbox database leeggemaakt"

echo ""
echo "▶ Stap 5: .env wissen (klantspecifiek)..."
if [ -f ~/lc-stack/.env ]; then
    cp ~/lc-stack/.env "$BACKUP_DIR/.env.backup"
    rm ~/lc-stack/.env
    echo "  ✓ .env verwijderd (backup in $BACKUP_DIR)"
else
    echo "  ℹ Geen .env gevonden"
fi

echo ""
echo "▶ Stap 6: Tijdelijke bestanden opruimen..."
# Geüploade bestanden in OWUI
docker exec openwebui find /app/backend/data/uploads -type f -delete 2>/dev/null && \
    echo "  ✓ OWUI uploads geleegd" || echo "  ℹ Geen uploads map"

echo ""
echo "▶ Stap 7: Containers herstarten..."
docker compose up -d
sleep 5
docker compose ps

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║   ✅ MASTER RESET VOLTOOID                            ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Bewaard:  Software, Docker images, AI-modellen,     ║"
echo "║            OWUI config, modellen, tools, filters     ║"
echo "║  Gewist:   Accounts, chats, mailboxen, .env, uploads ║"
echo "║  Backup:   $BACKUP_DIR"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo "Het systeem is klaar als MASTER SSD om te klonen."
echo "Na klonen bij klant: voer 'bash ~/lc-stack/scripts/setup_klant.sh' uit."
