#!/usr/bin/env bash
# Gera trafego de exemplo contra a API para popular os dashboards.
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
REQUESTS="${REQUESTS:-300}"

echo "Gerando $REQUESTS requisicoes em $BASE_URL ..."
for _ in $(seq 1 "$REQUESTS"); do
  curl -s -o /dev/null "$BASE_URL/work?fail=0.1&delay=0.05" || true
done
echo "Pronto."
