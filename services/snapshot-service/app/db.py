from typing import Any, Dict, Optional
import json
import psycopg
from psycopg.rows import dict_row
from .config import settings

def _dsn() -> str:
    return (
        f"host={settings.postgres_host} port={settings.postgres_port} "
        f"dbname={settings.postgres_db} user={settings.postgres_user} password={settings.postgres_password}"
    )

def insert_snapshot(initiative_id: str, snapshot: Dict[str, Any], quality: Dict[str, Any]) -> int:
    with psycopg.connect(_dsn(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO initiative_snapshots (initiative_id, snapshot, quality)
                VALUES (%s, %s::jsonb, %s::jsonb)
                RETURNING id
                """,
                (initiative_id, json.dumps(snapshot), json.dumps(quality)),
            )
            row = cur.fetchone()
            conn.commit()
            return int(row["id"])

def get_latest_snapshot(initiative_id: str) -> Optional[Dict[str, Any]]:
    with psycopg.connect(_dsn(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, initiative_id, snapshot, quality, created_at
                FROM initiative_snapshots
                WHERE initiative_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (initiative_id,),
            )
            row = cur.fetchone()
            return row
