#!/usr/bin/env bash
set -euo pipefail

# -------- configuration --------
DB_HOST="localhost"
DB_PORT="6543"
DB_NAME="athlete_market"
DB_USER="athlete_user"
export PGPASSWORD="athlete_password"

# Input file
INPUT_DIR="data"
INPUT_FILE="${INPUT_DIR}/backup.sql"

# -------- sanity checks --------
if [[ ! -f "${INPUT_FILE}" ]]; then
  echo "Backup file not found:"
  echo "  ${INPUT_FILE}"
  exit 1
fi

echo "Restoring database from:"
echo "  ${INPUT_FILE}"

# -------- restore database --------
# Notes:
# - ON_ERROR_STOP stops on first failure
# - UTF8 client encoding matches the dump
# - Uses psql because this is a plain .sql file

psql \
  --host="${DB_HOST}" \
  --port="${DB_PORT}" \
  --username="${DB_USER}" \
  --dbname="${DB_NAME}" \
  --set=ON_ERROR_STOP=on \
  --single-transaction \
  --encoding=UTF8 \
  < "${INPUT_FILE}"

echo "Database restore completed successfully."
