#!/bin/bash
# LocalCompute Fresh Install Script
# Ubuntu 22.04 / 24.04 LTS + NVIDIA GPU
# Gebruik: curl -s https://raw.githubusercontent.com/Lonobers88/lc-stack/main/install.sh | bash

set -e

echo "=============================================="
echo "  LocalCompute AI — Fresh Install"
echo "  github.com/Lonobers88/lc-stack"
echo "=============================================="
echo ""

# ---- 1. Systeem updates ----
echo "[1/8] Systeem updaten..."
apt-get update -qq
apt-get install -y -qq curl git ca-certificates gnupg lsb-release apt-transport-https

# ---- 2. Docker installeren ----
echo "[2/8] Docker installeren..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
        > /etc/apt/sources.list.d/docker.list
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    echo "  Docker geinstalleerd"
else
    echo "  Docker al aanwezig, skip"
fi

# Voeg lc user toe aan docker groep
useradd -m -s /bin/bash lc 2>/dev/null || true
usermod -aG docker lc

# ---- 3. NVIDIA Container Toolkit ----
echo "[3/8] NVIDIA Container Toolkit installeren..."
if ! command -v nvidia-smi &> /dev/null; then
    echo "  WAARSCHUWING: nvidia-smi niet gevonden. GPU drivers handmatig installeren na reboot."
    echo "  Installeer eerst: ubuntu-drivers autoinstall && reboot"
    echo "  Daarna dit script opnieuw runnen."
    GPU_READY=false
else
    GPU_READY=true
    if ! dpkg -l | grep -q nvidia-container-toolkit; then
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit.gpg
        curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit.gpg] https://#g' \
            > /etc/apt/sources.list.d/nvidia-container-toolkit.list
        apt-get update -qq
        apt-get install -y -qq nvidia-container-toolkit
        nvidia-ctk runtime configure --runtime=docker
        systemctl restart docker
        echo "  NVIDIA Container Toolkit geinstalleerd"
    else
        echo "  NVIDIA toolkit al aanwezig, skip"
    fi
fi

# ---- 4. Stack clonen ----
echo "[4/8] Stack ophalen van GitHub..."
STACK_DIR="/home/lc/lc-stack"
if [ -d "$STACK_DIR" ]; then
    echo "  Map bestaat al, git pull..."
    cd "$STACK_DIR"
    sudo -u lc git pull origin main
else
    sudo -u lc git clone https://github.com/Lonobers88/lc-stack "$STACK_DIR"
fi
cd "$STACK_DIR"

# ---- 5. .env aanmaken indien niet aanwezig ----
echo "[5/8] Configuratie voorbereiden..."
if [ ! -f "$STACK_DIR/.env" ]; then
    cat > "$STACK_DIR/.env" << 'EOF'
# LocalCompute configuratie
# Vul in via Setup Assistent in Open WebUI

M365_TENANT_ID=common
M365_CLIENT_ID=
M365_CLIENT_SECRET=
M365_REDIRECT_URI=http://localhost:8010/auth/callback
M365_SCOPES=offline_access https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/User.Read
EOF
    echo "  .env aangemaakt (leeg, invullen via Setup Assistent)"
else
    echo "  .env al aanwezig, skip"
fi

# ---- 6. Ollama modellen downloaden ----
echo "[6/8] Stack starten en modellen downloaden..."
cd "$STACK_DIR"
docker compose up -d ollama qdrant

echo "  Wachten tot Ollama klaar is..."
sleep 10
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        break
    fi
    sleep 2
done

echo "  Qwen3:14b downloaden (dit duurt even ~9GB)..."
docker exec ollama ollama pull qwen3:14b

echo "  Embedding model downloaden (~1.5GB)..."
docker exec ollama ollama pull bge-m3:latest

# ---- 7. Volledige stack starten ----
echo "[7/9] Volledige stack starten..."
docker compose up -d

sleep 10
echo ""
echo "Container status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}"


# ---- 8. OWUI configuratie laden ----
echo "[8/9] Open WebUI configuratie laden (modellen, tools, filters)..."
sleep 5

# Wacht tot OWUI beschikbaar is
echo "  Wachten tot Open WebUI klaar is..."
for i in $(seq 1 30); do
    if curl -s http://localhost:3000/health > /dev/null 2>&1; then
        break
    fi
    sleep 3
done

echo ""
echo "  Open WebUI is bereikbaar."
echo ""
echo "  STAP: Maak eerst een admin account aan via http://$LOCAL_IP:3000"
echo "  Daarna run je eenmalig:"
echo ""
echo "    docker cp $STACK_DIR/install/seed_owui.py openwebui:/tmp/seed_owui.py"
echo "    docker cp $STACK_DIR/install/owui_seed.json openwebui:/tmp/owui_seed.json"
echo "    docker exec openwebui python3 /tmp/seed_owui.py"
echo ""
echo "  Dit laadt alle workspace modellen, tools en filters automatisch."
echo ""

# ---- 9. Klaar ----
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "=============================================="
echo "  Installatie voltooid!"
echo ""
echo "  Open WebUI:  http://$LOCAL_IP:3000"
echo "  m365 API:    http://$LOCAL_IP:8010"
echo ""
echo "  Volgende stappen:"
echo "  1. Ga naar http://$LOCAL_IP:3000"
echo "  2. Maak een admin account aan"
echo "  3. Gebruik de Setup Assistent voor koppelingen"
if [ "$GPU_READY" = false ]; then
echo ""
echo "  LET OP: GPU drivers nog niet geinstalleerd!"
echo "  Run: sudo ubuntu-drivers autoinstall && sudo reboot"
echo "  Daarna draaien Ollama en Whisper op GPU."
fi
echo "=============================================="
