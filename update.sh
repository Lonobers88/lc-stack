#!/bin/bash
# LocalCompute Stack Updater v1.0
# Usage: ./update.sh [--force]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKUP_DIR="$HOME/lc-stack-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${GREEN}=== LocalCompute Stack Updater ===${NC}"
echo "Timestamp: $TIMESTAMP"

# Check if in lc-stack directory
if [ ! -f "$HOME/lc-stack/docker-compose.yml" ]; then
    echo -e "${RED}Error: lc-stack not found in $HOME/lc-stack${NC}"
    exit 1
fi

cd $HOME/lc-stack

# Step 1: Backup
echo -e "\n${YELLOW}Step 1: Creating backup...${NC}"
mkdir -p $BACKUP_DIR

# Backup OWUI database
OWUI_DB="/var/lib/docker/volumes/lc-stack_openwebui/_data/webui.db"
if [ -f "$OWUI_DB" ]; then
    sudo cp $OWUI_DB $BACKUP_DIR/webui.db.$TIMESTAMP.backup
    echo "Database backed up"
fi

# Backup current compose
cp docker-compose.yml $BACKUP_DIR/docker-compose.yml.$TIMESTAMP.backup
echo "docker-compose.yml backed up"

# Backup current git state
git rev-parse HEAD > $BACKUP_DIR/git-commit.$TIMESTAMP.backup
echo "Git commit saved"

# Step 2: Git pull
echo -e "\n${YELLOW}Step 2: Pulling latest changes...${NC}"
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ] && [ "$1" != "--force" ]; then
    echo -e "${GREEN}Already up to date!${NC}"
    exit 0
fi

git pull origin main
echo "Git pull complete"

# Step 3: Update containers
echo -e "\n${YELLOW}Step 3: Updating containers...${NC}"
sudo docker-compose pull
sudo docker-compose down
echo "Old containers stopped"

# Step 4: Start new containers
echo -e "\n${YELLOW}Step 4: Starting new containers...${NC}"
sudo docker-compose up -d
echo "Containers started"

# Step 5: Health check
echo -e "\n${YELLOW}Step 5: Health check...${NC}"
sleep 15

CONTAINERS=("openwebui" "ollama" "qdrant" "m365-mail-service" "cloudflared")
ALL_HEALTHY=true

for container in "${CONTAINERS[@]}"; do
    STATUS=$(sudo docker ps --filter "name=$container" --format "{{.Status}}" | grep -o "Up" || true)
    if [ "$STATUS" = "Up" ]; then
        echo -e "${GREEN}✓ $container running${NC}"
    else
        echo -e "${RED}✗ $container not running${NC}"
        ALL_HEALTHY=false
    fi
done

if [ "$ALL_HEALTHY" = true ]; then
    echo -e "\n${GREEN}=== Update successful! ===${NC}"
    echo "Access Open WebUI at: http://100.76.154.51:3000"
else
    echo -e "\n${RED}=== Update failed! Rolling back... ===${NC}"
    git reset --hard $LOCAL
    sudo cp $BACKUP_DIR/docker-compose.yml.$TIMESTAMP.backup docker-compose.yml
    sudo docker-compose down
    sudo docker-compose up -d
    
    if [ -f "$BACKUP_DIR/webui.db.$TIMESTAMP.backup" ]; then
        sudo cp $BACKUP_DIR/webui.db.$TIMESTAMP.backup $OWUI_DB
    fi
    
    echo -e "${YELLOW}Rollback complete${NC}"
    exit 1
fi
