# LocalCompute AI - Deployment Guide

Handleiding voor installatie, configuratie en onderhoud van de LocalCompute AI stack.

---

## 1. Prerequisites

### Hardware Minima
| Component | Minimum | Aanbevolen |
|-----------|---------|------------|
| GPU | NVIDIA RTX 4090 (24GB VRAM) | NVIDIA RTX 5090 (32GB VRAM) |
| RAM | 32 GB | 64 GB |
| Disk | 500 GB SSD | 2 TB NVMe SSD |
| CPU | 8 cores | 16+ cores |
| Netwerk | 1 Gbps LAN | 10 Gbps LAN |

### Software Vereisten
- Ubuntu 22.04 LTS of 24.04 LTS
- NVIDIA GPU drivers (>= 545.xx)
- NVIDIA Container Toolkit
- Docker & Docker Compose v2
- Git
- SSH toegang

---

## 2. Installation

### Stap 1: Hardware voorbereiden
1. Installeer Ubuntu Server met automatische updates
2. Configureer statisch IP-adres
3. Zet SSH key-based authentication op
4. Update het systeem: `sudo apt update && sudo apt upgrade -y`

### Stap 2: NVIDIA drivers installeren
```bash
# Installeer NVIDIA drivers
sudo ubuntu-drivers autoinstall

# Reboot
sudo reboot

# Controleer of GPU werkt
nvidia-smi
```

### Stap 3: LocalCompute stack deployen
```bash
# Clone repository
cd ~
git clone https://github.com/Lonobers88/lc-stack.git
cd lc-stack

# Run install script (running as root)
sudo bash install.sh

# Script voert uit:
# - Docker + Docker Compose installatie
# - NVIDIA Container Toolkit setup
# - Stack containers opstarten
```

### Stap 4: Post-install verificatie
```bash
# Controleer containers
docker ps

# Check GPU offloading
docker exec ollama nvidia-smi

# Test Ollama API
curl http://localhost:11434/api/tags
```

---

## 3. Configuration

### Eerste keer inloggen Open WebUI
1. Open browser: `http://<server-ip>:3000`
2. Maak admin account aan:
   - Email: admin@bedrijf.nl
   - Wachtwoord: (sterk wachtwoord)
3. Log in als admin

### Workspace Modellen Configureren
```bash
# Importeer LocalCompute configuratie
docker cp install/seed_owui.py openwebui:/tmp/
docker cp install/owui_seed.json openwebui:/tmp/
docker exec openwebui python3 /tmp/seed_owui.py
```

Dit importeert:
- **AI Assistent** (lc-medewerker) - Algemene vragen, HR, email
- **Setup Assistent** (lc-setup) - Configuratie van koppelingen

### Model Selecteren
1. Ga naar Workspace (linksboven)
2. Selecteer "AI Assistent"
3. Model zou op "gemma4:26b" moeten staan

### Knowledge Base Setup
1. Ga naar Knowledge in OWUI
2. Create Collection: "Bedrijfsdocumenten"
3. Upload documenten:
   - Personeelshandboek PDF
   - CAO documenten
   - Interne richtlijnen
4. Koppel aan AI Assistent model

---

## 4. First-time Setup Checklist

- [ ] Admin account aangemaakt
- [ ] Modellen geïmporteerd via seed_owui.py
- [ ] Models kunnen chatten met: `Hallo, ben je er?`
- [ ] Knowledge base documenten geüpload
- [ ] Test vraag stellen over je eigen documenten
- [ ] M365/E koppeling geconfigureerd via Setup Assistent
- [ ] Tailscale ingeschakeld voor remote access
- [ ] Health check script werkt: `./healthcheck.sh`

---

## 5. Maintenance

### Dagelijks
- Check automatische health logs: `tail -f ~/lc-stack/logs/health.log`
- Monitor GPU temps: `nvidia-smi`

### Wekelijks
- Update stack: `./update.sh`
- Review disk usage: `df -h`
- Backup check: `ls -la ~/lc-stack-backups/`

### Maandelijks
- System updates: `sudo apt update && sudo apt upgrade`
- Model cleanup: `docker exec ollama ollama list` (verwijder ongebruikte)
- Log rotatie: log files > 100MB truncaten

### Backup Strategie
Backups worden automatisch gemaakt bij updates:
- Locatie: `~/lc-stack-backups/`
- Bestanden: webui.db, docker-compose.yml, git commit
- Retentie: handmatig opruimen na succesvolle update

---

## 6. Troubleshooting

### Probleem: Model draait op CPU ipv GPU
**Symptoom**: Traag (10 tok/s), `ollama ps` toont "100% CPU"

**Diagnose**:
```bash
docker exec ollama nvidia-smi  # Fails = NVML error
docker exec ollama ollama ps   # Toont CPU%
```

**Oplossing**:
```bash
# Stop en verwijder container (forceer recreate met GPU runtime)
cd ~/lc-stack
docker compose stop ollama
docker compose rm -f ollama
docker compose up -d ollama

# Verifieer
docker exec ollama nvidia-smi  # Moet werken
```

**Preventie**: Zorg dat `/etc/docker/daemon.json` default runtime "nvidia" heeft:
```json
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime"
    }
  }
}
```

### Probleem: Open WebUI niet bereikbaar
**Symptoom**: `curl localhost:3000` timeout

**Oplossing**:
```bashndocker logs openwebui --tail 50
# Check of container draait
docker ps | grep openwebui

# Restart indien nodig
docker restart openwebui
```

### Probleem: Geheugen vol (OOM)
**Symptoom**: Model crasht, "out of memory" in logs

**Oplossing**:
- Kleinere model gebruiken (qwen3.5:14b ipv 35b)
- Of meerdere GPUs/nodes toevoegen
- Context lengte verminderen in model params

### Probleem: Knowledge base werkt niet
**Symptoom**: Model weet niks van je documenten

**Oplossing**:
1. Check of documents zijn geüpload
2. Check RAG filter actief: `Admin > Functions > lc_rag_grounding`
3. Model moet "knowledgeIds" hebben in database
4. Restart Open WebUI na wijzigingen

---

## 7. Contact & Support

Voor technische issues:
- Check logs: `docker logs <container>`
- Health check: `./healthcheck.sh`
- GitHub: https://github.com/Lonobers88/lc-stack/issues

---

*Document versie: 1.0 | Laatste update: 2026-04-12*
