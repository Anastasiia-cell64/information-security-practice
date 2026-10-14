#!/usr/bin/env bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }

mkdir -p reports

echo "== 1. Секрети =="
if [ -f .env ]; then
    ok ".env є"
    grep -q "^\.env" .gitignore && ok ".env у .gitignore" || warn ".env відсутній у .gitignore"
else
    warn ".env відсутній"
fi

echo "== 2. Docker =="
if [ -f Dockerfile ]; then
    grep -q "USER" Dockerfile && ok "Dockerfile: USER (non-root)" || fail "Dockerfile: відсутній USER"
    grep -q "HEALTHCHECK" Dockerfile && ok "Dockerfile: HEALTHCHECK" || warn "Dockerfile: немає HEALTHCHECK"
fi

echo "== 3. HTTPS і заголовок =="
curl -k -s https://localhost/health >/dev/null && ok "HTTPS працює" || warn "https://localhost недоступний"

echo "== 4. Залежності, код, образ =="
IMAGE="information-security-practice-api:latest"

if docker info >/dev/null 2>&1; then
    MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd -P)":/src -w /src python:3.11-slim sh -c \
        "pip install -q pip-audit >/dev/null 2>&1 && pip-audit -r requirements.txt" > reports/pip-audit.txt 2>&1 \
        && ok "pip-audit: вразливостей не знайдено" || warn "pip-audit: є знахідки (reports/pip-audit.txt)"

    MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd -P)":/src -w /src python:3.11-slim sh -c \
        "pip install -q bandit >/dev/null 2>&1 && bandit -r app -ll -q" > reports/bandit-high.txt 2>&1 \
        && ok "Bandit: HIGH-проблем немає" || fail "Bandit: є HIGH (reports/bandit-high.txt)"

    if docker image inspect "$IMAGE" >/dev/null 2>&1; then
        MSYS_NO_PATHCONV=1 docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.56.2 image \
            --severity CRITICAL --ignore-unfixed --exit-code 1 "$IMAGE" > reports/trivy-critical.txt 2>&1 \
            && ok "Trivy: CRITICAL з виправленням немає" || warn "Trivy: є CRITICAL (reports/trivy-critical.txt)"
    else
        warn "образ $IMAGE не знайдено"
    fi
else
    warn "Docker daemon недоступний"
fi