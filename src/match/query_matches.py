"""Query vehicle-driver matching data from PostgreSQL.

Based on Terminal (vehicle) with Fleet ID = 29 (Kurly/R).
Shows which drivers are assigned to each vehicle.
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
load_dotenv(dotenv_path=PROJECT_DIR / ".env")

DATA_FILE = SCRIPT_DIR / "data.txt"
FLEET_ID = 29
START_DATE = "2026-01-20"


def get_db_config():
    """Get database configuration from environment variables."""
    return {
        "host": os.getenv("PROD_DB_HOST"),
        "port": int(os.getenv("PROD_DB_PORT", "5432")),
        "database": os.getenv("PROD_DB_NAME"),
        "user": os.getenv("PROD_DB_USER"),
        "password": os.getenv("PROD_DB_PASSWORD"),
    }


def query_matches(work_date: str) -> list:
    """
    Query vehicle-driver matches for a specific work date.

    Based on Terminal (vehicle) with Fleet ID = 29.
    Returns: date, vehicle_number, operation_type, driver_name, match_status
    """
    config = get_db_config()
    conn = psycopg2.connect(**config)
    cursor = conn.cursor()

    query = """
        SELECT
            %(work_date)s as date,
            t.plate_number as vehicle_number,
            t.operation_type,
            COALESCE(d.name, '') as driver_name,
            CASE WHEN dvm.id IS NOT NULL THEN 'O' ELSE 'X' END as match_status
        FROM dashboard_terminal t
        LEFT JOIN schedule_drivervehiclematch dvm
            ON dvm.vehicle_id = t.id
            AND dvm.work_date = %(work_date)s::date
        LEFT JOIN core_user u ON dvm.user_id = u.id
        LEFT JOIN documents_document d ON u.delivery_user_id = d.id
        WHERE t.fleet_id = %(fleet_id)s
          AND t.is_deleted = false
        ORDER BY match_status DESC, t.plate_number;
    """

    cursor.execute(query, {
        "work_date": work_date,
        "fleet_id": FLEET_ID
    })

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results


def append_data(work_date: str):
    """Query and append data for specific date."""
    remove_date(work_date)
    results = query_matches(work_date)

    with open(DATA_FILE, "a", encoding="utf-8") as f:
        for date, vehicle, op_type, driver, match in results:
            f.write(f"{date}|{vehicle}|{op_type}|{driver}|{match}\n")

    print(f"Added {len(results)} records for {work_date}")


def remove_date(work_date: str):
    """Remove existing data for specific date."""
    if not DATA_FILE.exists():
        return

    lines = DATA_FILE.read_text(encoding="utf-8").splitlines()
    new_lines = [l for l in lines if not l.startswith(f"{work_date}|")]
    DATA_FILE.write_text("\n".join(new_lines) + ("\n" if new_lines else ""), encoding="utf-8")


def refresh_all():
    """Refresh all data from START_DATE to yesterday."""
    start_dt = datetime.strptime(START_DATE, "%Y-%m-%d")
    yesterday = datetime.now() - timedelta(days=1)

    DATA_FILE.write_text("")

    current = start_dt
    while current <= yesterday:
        date_str = current.strftime("%Y-%m-%d")
        try:
            append_data(date_str)
        except Exception as e:
            print(f"Failed to query {date_str}: {e}")
        current += timedelta(days=1)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python query_matches.py [today|all|YYYY-MM-DD]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "today":
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        append_data(yesterday)
    elif cmd == "all":
        refresh_all()
    else:
        append_data(cmd)


if __name__ == "__main__":
    main()
