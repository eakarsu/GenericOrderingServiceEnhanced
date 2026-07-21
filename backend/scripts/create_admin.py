"""Provision one explicitly acknowledged administrator without demo data."""
import os
import psycopg2
from passlib.hash import bcrypt

if os.environ.get("BOOTSTRAP_ACKNOWLEDGEMENT") != "create-initial-admin":
    raise SystemExit("BOOTSTRAP_ACKNOWLEDGEMENT=create-initial-admin is required")
email = (os.environ.get("PROVISION_ADMIN_EMAIL") or os.environ.get("ADMIN_EMAIL") or "").strip().lower()
password = os.environ.get("PROVISION_ADMIN_PASSWORD") or os.environ.get("ADMIN_PASSWORD") or ""
name = (os.environ.get("PROVISION_ADMIN_NAME") or "Runtime Acceptance").strip().split(" ", 1)
if not email or len(password) < 12:
    raise SystemExit("Admin email and password of at least 12 characters are required")
url = os.environ.get("SYNC_DATABASE_URL") or os.environ.get("DATABASE_URL")
if not url: raise SystemExit("DATABASE_URL is required")
password_hash = bcrypt.using(rounds=12).hash(password)
with psycopg2.connect(url) as connection:
    with connection.cursor() as cursor:
        cursor.execute("""INSERT INTO users(username,email,password_hash,first_name,last_name,role,is_active,is_verified)
          VALUES(%s,%s,%s,%s,%s,'admin',TRUE,TRUE)
          ON CONFLICT(email) DO UPDATE SET password_hash=EXCLUDED.password_hash,role='admin',is_active=TRUE,is_verified=TRUE
          RETURNING id""", (email, email, password_hash, name[0], name[1] if len(name)>1 else ""))
        user_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO user_settings(user_id) VALUES(%s) ON CONFLICT(user_id) DO NOTHING", (user_id,))
print(f"Provisioned ordering administrator for {email}")
