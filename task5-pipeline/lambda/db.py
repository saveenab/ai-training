import logging
import os
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "recalls_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "postgres"),
    )

def upsert_recalls(conn, records: list) -> int:
    if not records:
        logger.info("No records to upsert.")
        return 0
    
    seen = {}
    for r in records:
        seen[r["recall_id"]] = r
    records = list(seen.values())
    logger.info(f"After deduplication: {len(records)} unique records")

    values = [
        (
            r["recall_id"],
            r["title"],
            r["category"],
            r["component"],
            r["description"],
            r["consequence"],
            r["remedy"],
            r["report_date"],
            r["make"],
            r["model"],
            r["year"],
        )
        for r in records
    ]

    sql = """
        INSERT INTO recalls (
            recall_id, title, category, component, description,
            consequence, remedy, report_date, make, model, year
        )
        VALUES %s
        ON CONFLICT (recall_id) DO UPDATE SET
            title       = EXCLUDED.title,
            description = EXCLUDED.description,
            consequence = EXCLUDED.consequence,
            remedy      = EXCLUDED.remedy,
            updated_at  = NOW()
    """

    with conn.cursor() as cur:
        execute_values(cur, sql, values)
        affected = cur.rowcount

    conn.commit()
    logger.info(f"Upserted {affected} records.")
    return affected

def get_record_count(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM recalls;")
        return cur.fetchone()[0]
    
if __name__ == "__main__":
    import sys
    sys.path.insert(0, "lambda")
    from nhtsa_fetcher import fetch_all_recalls

    logging.basicConfig(level=logging.INFO)

    print("Fetching recalls from NHTSA...")
    records = fetch_all_recalls()
    print(f"Fetched {len(records)} records")

    print("Connecting to database...")
    conn = get_connection()
    print("Connected!")

    print("Upserting records...")
    affected = upsert_recalls(conn, records)

    count = get_record_count(conn)
    print(f"\n Done! Records in database: {count}")
    conn.close()