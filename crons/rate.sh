#!/bin/bash
set -euo pipefail

HC_URL="https://hc-ping.com/242d9d39-6841-40dc-a664-29c8c66f2fe6"

hc_ping() {
  curl -fsS -m 10 -o /dev/null "${HC_URL}$1"
}

hc_log() {
  local msg="$1"
  curl -fsS -m 10 -o /dev/null -X POST "${HC_URL}/log" --data-raw "$msg"
}

exit_status=0

on_err() {
  exit_status=$?
  hc_log "rate cron failed at '${BASH_COMMAND:-unknown}' (exit ${exit_status})" || true
  hc_ping "/fail" || true
  exit "${exit_status}"
}
trap 'on_err' ERR

on_exit() {
  local status=${exit_status:-$?}
  hc_ping "/${status}" || true
}
trap 'on_exit' EXIT

hc_ping "/start" || true
hc_log "rate cron started" || true

curl -fsS -m 30 -X POST http://localhost:3000/api/rate-cron \
  -H "Authorization: Bearer 123"

hc_log "rate cron finished" || true
