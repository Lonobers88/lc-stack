#!/bin/bash
# LocalCompute Health Check Script
# Checks: Ollama, Open WebUI, GPU, Docker, Disk, RAM
# Returns: JSON output + exit code 0 (OK) or 1 (FAIL)

set -e

TIMESTAMP=$(date -Iseconds)
LOG_FILE="/home/lc/lc-stack/logs/health.log"
STATUS="OK"
FAILURES=()

# Helper functions
check_pass() { echo "{\"check\":\"$1\",\"status\":\"OK\",\"detail\":\"$2\"}"; }
check_fail() { echo "{\"check\":\"$1\",\"status\":\"FAIL\",\"detail\":\"$2\"}"; STATUS="FAIL"; FAILURES+=("$1"); }

# Start JSON array
RESULTS="["

# 1. Check Ollama API
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    RESULTS+=$(check_pass "ollama_api" "reachable")
else
    RESULTS+=$(check_fail "ollama_api" "not reachable")
fi
RESULTS+=","

# 2. Check Open WebUI
if curl -s http://localhost:3000/api/version > /dev/null 2>&1; then
    RESULTS+=$(check_pass "openwebui" "reachable")
else
    RESULTS+=$(check_fail "openwebui" "not reachable")
fi
RESULTS+=","

# 3. Check GPU
if nvidia-smi > /dev/null 2>&1; then
    GPU_MEM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | tr -d " ")
    RESULTS+=$(check_pass "gpu" "RTX 5090 active, ${GPU_MEM}MiB used")
else
    RESULTS+=$(check_fail "gpu" "nvidia-smi failed")
fi
RESULTS+=","

# 4. Check Docker containers
MISSING_CONTAINERS=()
for container in ollama openwebui qdrant m365-mail-service whisper searxng cloudflared; do
    if ! docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
        MISSING_CONTAINERS+=("$container")
    fi
done

if [ ${#MISSING_CONTAINERS[@]} -eq 0 ]; then
    RESULTS+=$(check_pass "docker_containers" "all 7 running")
else
    RESULTS+=$(check_fail "docker_containers" "missing: ${MISSING_CONTAINERS[*]}")
fi
RESULTS+=","

# 5. Check Disk usage
DISK_USAGE=$(df / | tail -1 | awk "{print \$5}" | tr -d "%")
if [ "$DISK_USAGE" -lt 90 ]; then
    RESULTS+=$(check_pass "disk_usage" "${DISK_USAGE}%")
else
    RESULTS+=$(check_fail "disk_usage" "${DISK_USAGE}% (CRITICAL)")
fi
RESULTS+=","

# 6. Check RAM usage
RAM_USAGE=$(free | grep Mem | awk "{printf \"%.0f\", \$3/\$2 * 100.0}")
if [ "$RAM_USAGE" -lt 90 ]; then
    RESULTS+=$(check_pass "ram_usage" "${RAM_USAGE}%")
else
    RESULTS+=$(check_fail "ram_usage" "${RAM_USAGE}% (CRITICAL)")
fi

# Close JSON array
RESULTS+="]"

# Output JSON
OUTPUT="{\"timestamp\":\"$TIMESTAMP\",\"overall\":\"$STATUS\",\"checks\":$RESULTS}"
echo "$OUTPUT"

# Log to file
echo "$OUTPUT" >> "$LOG_FILE"

# Return exit code
if [ "$STATUS" = "OK" ]; then
    exit 0
else
    exit 1
fi
