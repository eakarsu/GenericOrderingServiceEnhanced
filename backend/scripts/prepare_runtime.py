"""Prepare the isolated acceptance database using additive migrations only."""
import os
import subprocess
import sys
from pathlib import Path
import psycopg2

root = Path(__file__).resolve().parents[2]
for raw_line in (root / ".env").read_text().splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    if key.strip() not in os.environ:
        os.environ[key.strip()] = value.strip().strip("\"'")
if os.environ.get("ALLOW_SCHEMA_MIGRATION") != "true":
    raise SystemExit("ALLOW_SCHEMA_MIGRATION=true is required")
subprocess.run([sys.executable, str(root / "backend/scripts/migrate.py")], check=True, cwd=root)
subprocess.run([sys.executable, str(root / "backend/scripts/create_admin.py")], check=True, cwd=root)
url = os.environ.get("SYNC_DATABASE_URL") or os.environ.get("DATABASE_URL")
with psycopg2.connect(url) as connection:
    with connection.cursor() as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS ordering_runtime_ai_results (
          id BIGSERIAL PRIMARY KEY, user_id BIGINT NOT NULL REFERENCES users(id), input JSONB NOT NULL,
          result JSONB NOT NULL, model TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )""")
