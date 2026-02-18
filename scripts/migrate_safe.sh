#!/usr/bin/env bash
# Safe migrator: resolves "Conflicting migrations" then runs migrate.
# Run from project root: ./scripts/migrate_safe.sh

set -e
cd "$(dirname "$0")/.."
out=$(mktemp)
mig_out=$(mktemp)
trap 'rm -f "$out" "$mig_out"' EXIT

echo ">>> Checking for migration conflicts..."
if ! python manage.py makemigrations --dry-run --noinput > "$out" 2>&1; then
  if grep -q "Conflicting migrations" "$out" 2>/dev/null; then
    echo ">>> Conflicting migrations detected. Creating merge migration..."
    python manage.py makemigrations --merge --noinput
  else
    cat "$out"
    exit 1
  fi
fi

echo ">>> Applying migrations..."
if ! python manage.py migrate 2> "$mig_out"; then
  cat "$mig_out"
  if grep -q "already exists" "$mig_out" 2>/dev/null; then
    echo ""
    echo ">>> Table already exists? Mark that migration as applied with:"
    echo "    python manage.py migrate <app_name> <migration_name> --fake"
    echo "    Then run: python manage.py migrate"
    echo "    See README section 'Migrations' for details."
  elif grep -q "Access denied\|OperationalError\|connect" "$mig_out" 2>/dev/null; then
    echo ""
    echo ">>> Database connection failed. Check .env: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST."
  fi
  exit 1
fi

echo ">>> Migrations complete."
python manage.py check
