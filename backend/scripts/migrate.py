"""Apply additive migrations only when invoked explicitly by operations tooling."""
import os
from pathlib import Path
import psycopg2

url = os.environ.get("SYNC_DATABASE_URL") or os.environ.get("DATABASE_URL")
if not url: raise SystemExit("DATABASE_URL is required")
migration_dir = Path(__file__).resolve().parents[1] / "migrations"
with psycopg2.connect(url) as connection:
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW())")
        for migration in sorted(migration_dir.glob("*.sql")):
            cursor.execute("SELECT 1 FROM schema_migrations WHERE name=%s", (migration.name,))
            if cursor.fetchone(): continue
            sql = migration.read_text().strip()
            if sql.startswith("BEGIN;"): sql = sql[len("BEGIN;"):].strip()
            if sql.endswith("COMMIT;"): sql = sql[:-len("COMMIT;")].strip()
            cursor.execute(sql)
            cursor.execute("INSERT INTO schema_migrations(name) VALUES(%s)", (migration.name,))
            print(f"applied {migration.name}")
