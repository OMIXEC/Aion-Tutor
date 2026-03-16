#!/usr/bin/env python3
"""
Aion Tutor — Database Migration Runner

Applies pending SQL migrations from the migrations/ directory to Supabase.
Migrations are tracked in the public.schema_migrations table.

Usage:
  cd backend
  uv run python migrations/run_migrations.py [--dry-run]
"""
import os
import sys
import argparse
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

MIGRATIONS_DIR = Path(__file__).parent


def get_db():
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        print("❌ SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
        sys.exit(1)
    return create_client(url, key)


def get_applied_versions(db) -> set[str]:
    """Return set of already-applied migration versions."""
    try:
        res = db.table("schema_migrations").select("version").execute()
        return {row["version"] for row in (res.data or [])}
    except Exception:
        # Table doesn't exist yet — that's fine, V001 will create it
        return set()


def run_migrations(dry_run: bool = False):
    db = get_db()
    applied = get_applied_versions(db)

    # Find all .sql files sorted by version prefix (V001, V002, ...)
    migration_files = sorted(
        MIGRATIONS_DIR.glob("V*.sql"),
        key=lambda f: f.name
    )

    if not migration_files:
        print("ℹ️  No migration files found in migrations/")
        return

    pending = [f for f in migration_files if f.stem.split("__")[0] not in applied]

    if not pending:
        print(f"✅ All {len(migration_files)} migrations already applied.")
        return

    print(f"📋 Found {len(pending)} pending migration(s):")
    for f in pending:
        print(f"   • {f.name}")

    if dry_run:
        print("\n🔍 Dry-run mode — no changes made.")
        return

    print()
    for migration_file in pending:
        version = migration_file.stem.split("__")[0]
        name    = migration_file.stem
        sql     = migration_file.read_text(encoding="utf-8")

        print(f"▶  Applying {name}...", end=" ", flush=True)
        try:
            # Supabase doesn't expose raw SQL exec via Python client directly,
            # so we use the postgrest rpc call via the admin REST API
            # For full SQL access, use the Supabase Management API or psycopg2
            import httpx
            supabase_url = os.environ["SUPABASE_URL"]
            service_key  = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

            # Use the /rest/v1/rpc path won't work for raw DDL.
            # Use the direct postgres connection via asyncpg instead.
            _apply_via_postgres(sql, version)
            print("✅")
        except Exception as e:
            print(f"❌\n   Error: {e}")
            print("   Stopping migration run.")
            sys.exit(1)

    print(f"\n🎉 Applied {len(pending)} migration(s) successfully.")


def _apply_via_postgres(sql: str, version: str):
    """
    Apply SQL directly via asyncpg (bypasses Supabase client limitations for DDL).
    Falls back to manual Supabase SQL Editor instructions if no direct DB URL is set.
    """
    import asyncio
    import asyncpg

    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        # Construct from Supabase URL pattern
        supabase_url = os.environ.get("SUPABASE_URL", "")
        if "supabase.co" in supabase_url:
            # Extract project ref from URL: https://<ref>.supabase.co
            ref = supabase_url.replace("https://", "").split(".")[0]
            password = os.environ.get("SUPABASE_DB_PASSWORD", "")
            if not password:
                raise RuntimeError(
                    f"Cannot apply migration {version} directly. "
                    "Set DATABASE_URL=postgresql://postgres:<password>@db.<ref>.supabase.co:5432/postgres "
                    "OR run the SQL manually in the Supabase SQL Editor."
                )
            db_url = f"postgresql://postgres:{password}@db.{ref}.supabase.co:5432/postgres"
        else:
            raise RuntimeError("DATABASE_URL not set and cannot be derived from SUPABASE_URL.")

    async def _run():
        conn = await asyncpg.connect(db_url)
        try:
            await conn.execute(sql)
        finally:
            await conn.close()

    asyncio.run(_run())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aion Tutor Migration Runner")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview pending migrations without applying them."
    )
    args = parser.parse_args()

    print("═══════════════════════════════════════════════")
    print("   🗄️  Aion Tutor — Database Migration Runner   ")
    print("═══════════════════════════════════════════════")
    print(f"   Migrations dir: {MIGRATIONS_DIR}")
    print()

    run_migrations(dry_run=args.dry_run)
