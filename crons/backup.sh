#!/bin/bash
#
# Daily MongoDB backup -> Cloudflare R2.
#
# Делает сжатый дамп всей базы через mongodump, шифрует его age (если задан
# ключ) и заливает в R2-бакет по S3 API. Запускается раз в 24 часа
# (см. crons/README.md). Старые копии удаляет lifecycle-правило самого R2.
#
# Требуемые переменные окружения (берём из Doppler, как и остальные краны):
#   MONGODB_URI            - строка подключения к MongoDB (та же, что у ботов)
#   R2_ENDPOINT            - https://<account_id>.r2.cloudflarestorage.com
#   R2_BUCKET              - имя бакета для бэкапов
#   R2_ACCESS_KEY_ID       - Access Key ID R2 API-токена
#   R2_SECRET_ACCESS_KEY   - Secret Access Key R2 API-токена
# Необязательные:
#   BACKUP_AGE_RECIPIENT   - публичный age-ключ; если задан, дамп шифруется
#   HC_URL                 - URL проверки healthchecks.io для мониторинга
#
# Зависимости на VPS: mongodb-database-tools (mongodump), awscli, curl,
# age (только если включено шифрование).
#
set -euo pipefail

HC_URL="${HC_URL:-}"

hc_ping() {
  [ -n "$HC_URL" ] || return 0
  curl -fsS -m 10 -o /dev/null "${HC_URL}$1" || true
}

hc_log() {
  [ -n "$HC_URL" ] || return 0
  curl -fsS -m 10 -o /dev/null -X POST "${HC_URL}/log" --data-raw "$1" || true
}

on_err() {
  local err_status=$?
  hc_log "backup cron failed at '${BASH_COMMAND:-unknown}' (exit ${err_status})"
  hc_ping "/fail"
  exit "${err_status}"
}
trap 'on_err' ERR

# Чистим временные файлы и пингуем итоговый статус в healthchecks.
# Внутри EXIT-трапа $? равен коду выхода скрипта, каким бы путём он ни вышел.
on_exit() {
  local status=$?
  [ -n "${DUMP_FILE:-}" ] && rm -f "${DUMP_FILE}" "${DUMP_FILE}.age" || true
  hc_ping "/${status}"
}
trap 'on_exit' EXIT

# Проверяем обязательные переменные окружения.
: "${MONGODB_URI:?MONGODB_URI is not set}"
: "${R2_ENDPOINT:?R2_ENDPOINT is not set}"
: "${R2_BUCKET:?R2_BUCKET is not set}"
: "${R2_ACCESS_KEY_ID:?R2_ACCESS_KEY_ID is not set}"
: "${R2_SECRET_ACCESS_KEY:?R2_SECRET_ACCESS_KEY is not set}"

# awscli читает креды только из AWS_*-переменных, прокидываем из R2_*.
export AWS_ACCESS_KEY_ID="${R2_ACCESS_KEY_ID}"
export AWS_SECRET_ACCESS_KEY="${R2_SECRET_ACCESS_KEY}"

BACKUP_AGE_RECIPIENT="${BACKUP_AGE_RECIPIENT:-}"

# awscli v2.23+ по умолчанию считает CRC-чексуммы, которые понимает не каждый
# S3-совместимый сервис; для R2 включаем их только там, где это обязательно.
export AWS_REQUEST_CHECKSUM_CALCULATION=when_required
export AWS_RESPONSE_CHECKSUM_VALIDATION=when_required

hc_ping "/start"
hc_log "backup cron started"

TIMESTAMP="$(date -u +%Y-%m-%d_%H-%M-%S)"
DUMP_FILE="/tmp/roger-bot-db_${TIMESTAMP}.archive.gz"

# Снимаем сжатый дамп всей базы в один архив-файл.
mongodump --uri="${MONGODB_URI}" --archive="${DUMP_FILE}" --gzip

# Дамп содержит чувствительные данные (настроение, переписка поддержки),
# поэтому перед выгрузкой шифруем его age-ключом.
UPLOAD_FILE="${DUMP_FILE}"
if [ -n "${BACKUP_AGE_RECIPIENT}" ]; then
  age -r "${BACKUP_AGE_RECIPIENT}" -o "${DUMP_FILE}.age" "${DUMP_FILE}"
  UPLOAD_FILE="${DUMP_FILE}.age"
else
  hc_log "BACKUP_AGE_RECIPIENT is not set, uploading UNENCRYPTED dump"
fi

FILE_SIZE_BYTES="$(stat -c%s "${UPLOAD_FILE}" 2>/dev/null || stat -f%z "${UPLOAD_FILE}")"

# Заливаем архив в R2 по S3 API.
aws s3 cp "${UPLOAD_FILE}" "s3://${R2_BUCKET}/$(basename "${UPLOAD_FILE}")" \
  --endpoint-url "${R2_ENDPOINT}" \
  --region auto \
  --only-show-errors

hc_log "backup cron finished, uploaded ${FILE_SIZE_BYTES} bytes to ${R2_BUCKET}"
