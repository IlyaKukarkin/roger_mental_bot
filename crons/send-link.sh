#!/bin/bash
set -euo pipefail

HC_URL="https://hc-ping.com/c6dca0a2-907b-42d9-a1a8-2c659d1de922"

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
  hc_log "send-link cron failed at '${BASH_COMMAND:-unknown}' (exit ${exit_status})" || true
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
hc_log "send-link cron started" || true

curl -fsS -m 30 -X POST http://localhost:3000/api/send-link-cron \
  -H "Authorization: Bearer 123"

hc_log "send-link cron finished" || true
