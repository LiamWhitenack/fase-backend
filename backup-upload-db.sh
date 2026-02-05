#!/usr/bin/env bash
set -euo pipefail

# -------- configuration --------
DB_HOST="localhost"
DB_PORT="6543"
DB_NAME="athlete_market"
DB_USER="athlete_user"
export PGPASSWORD="athlete_password"

INPUT_DIR="data"
INPUT_FILE="${INPUT_DIR}/backup.sql"

# -------- sanity checks --------
if [[ ! -f "${INPUT_FILE}" ]]; then
  echo "Backup file not found:"
  echo "  ${INPUT_FILE}"
  exit 1
fi

echo "Dropping and recreating database: ${DB_NAME}"

psql \
  --host="${DB_HOST}" \
  --port="${DB_PORT}" \
  --username="${DB_USER}" \
  --dbname="postgres" \
  <<EOF
-- Kick everyone else off the DB
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '${DB_NAME}'
  AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS ${DB_NAME};
CREATE DATABASE ${DB_NAME};
EOF

echo "Restoring database from:"
echo "  ${INPUT_FILE}"

psql \
  --host="${DB_HOST}" \
  --port="${DB_PORT}" \
  --username="${DB_USER}" \
  --dbname="${DB_NAME}" \
  --set=ON_ERROR_STOP=on \
  < "${INPUT_FILE}"

echo "Database restore completed successfully."
