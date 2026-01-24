#!/usr/bin/env bash
set -euo pipefail

# -------- configuration --------
DB_HOST="localhost"
DB_PORT="6543"
DB_NAME="athlete_market"
DB_USER="athlete_user"
export PGPASSWORD="athlete_password"

# Output file (timestamped so you don't overwrite old dumps)
OUTPUT_DIR="data"
OUTPUT_FILE="${OUTPUT_DIR}/backup.sql"

# -------- ensure output directory exists --------
mkdir -p "${OUTPUT_DIR}"

# -------- dump database --------
# PGPASSWORD can be set here, or you can rely on:
#   - ~/.pgpass
#   - environment variables
#   - interactive prompt
#
# export PGPASSWORD="your_password"

pg_dump \
  --host="${DB_HOST}" \
  --port="${DB_PORT}" \
  --username="${DB_USER}" \
  --format=plain \
  --encoding=UTF8 \
  --no-owner \
  --no-privileges \
  "${DB_NAME}" \
  > "${OUTPUT_FILE}"

echo "Database dump written to:"
echo "  ${OUTPUT_FILE}"
