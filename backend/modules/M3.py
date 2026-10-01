import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path


# --------------------------------------------------
# DATABASE LOCATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "ledger.db"


# --------------------------------------------------
# CREATE DATABASE / TABLE
# --------------------------------------------------

def init_ledger():
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sequence_number INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            asset_name TEXT,
            input_hash TEXT,
            model_hash TEXT,
            output_hash TEXT,
            previous_hash TEXT,
            record_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

    print("Ledger initialized successfully.")
    print(f"Database: {DB_PATH}")


# --------------------------------------------------
# CALCULATE RECORD HASH
# --------------------------------------------------

def calculate_record_hash(record):
    data = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(data.encode("utf-8")).hexdigest()


# --------------------------------------------------
# ADD RECORD TO LEDGER
# --------------------------------------------------

def add_record(
    event_type,
    asset_name="",
    input_hash="",
    model_hash="",
    output_hash=""
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get previous record
    cursor.execute("""
        SELECT sequence_number, record_hash
        FROM audit_ledger
        ORDER BY sequence_number DESC
        LIMIT 1
    """)

    previous = cursor.fetchone()

    if previous:
        sequence_number = previous[0] + 1
        previous_hash = previous[1]
    else:
        sequence_number = 1
        previous_hash = "GENESIS"

    timestamp = datetime.now().isoformat()

    record = {
        "sequence_number": sequence_number,
        "timestamp": timestamp,
        "event_type": event_type,
        "asset_name": asset_name,
        "input_hash": input_hash,
        "model_hash": model_hash,
        "output_hash": output_hash,
        "previous_hash": previous_hash
    }

    record_hash = calculate_record_hash(record)

    cursor.execute("""
        INSERT INTO audit_ledger (
            sequence_number,
            timestamp,
            event_type,
            asset_name,
            input_hash,
            model_hash,
            output_hash,
            previous_hash,
            record_hash
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sequence_number,
        timestamp,
        event_type,
        asset_name,
        input_hash,
        model_hash,
        output_hash,
        previous_hash,
        record_hash
    ))

    conn.commit()
    conn.close()

    print(f"Record #{sequence_number} added.")
    print(f"Record hash: {record_hash}")

    return record_hash


# --------------------------------------------------
# VERIFY HASH CHAIN
# --------------------------------------------------

def verify_ledger():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sequence_number,
            timestamp,
            event_type,
            asset_name,
            input_hash,
            model_hash,
            output_hash,
            previous_hash,
            record_hash
        FROM audit_ledger
        ORDER BY sequence_number
    """)

    records = cursor.fetchall()
    conn.close()

    if not records:
        print("Ledger is empty.")
        return True

    expected_previous_hash = "GENESIS"

    for record in records:

        (
            sequence_number,
            timestamp,
            event_type,
            asset_name,
            input_hash,
            model_hash,
            output_hash,
            previous_hash,
            stored_hash
        ) = record

        # Check previous hash
        if previous_hash != expected_previous_hash:

            print(
                f"❌ TAMPERING DETECTED at record #{sequence_number}"
            )

            print("Reason: Previous hash mismatch.")

            return False

        # Reconstruct record
        data = {
            "sequence_number": sequence_number,
            "timestamp": timestamp,
            "event_type": event_type,
            "asset_name": asset_name,
            "input_hash": input_hash,
            "model_hash": model_hash,
            "output_hash": output_hash,
            "previous_hash": previous_hash
        }

        calculated_hash = calculate_record_hash(data)

        # Check record hash
        if calculated_hash != stored_hash:

            print(
                f"❌ TAMPERING DETECTED at record #{sequence_number}"
            )

            print("Reason: Record hash mismatch.")

            return False

        expected_previous_hash = stored_hash

    print("✅ Ledger verification successful.")
    print("No tampering detected.")

    return True


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("\n--- SatyaNetra M3 Provenance ---\n")

    init_ledger()

    add_record(
        event_type="MODEL_REGISTERED",
        asset_name="test_model.pt",
        model_hash="ABC123MODELHASH"
    )

    add_record(
        event_type="INFERENCE_CREATED",
        asset_name="image_001.jpg",
        input_hash="INPUT123",
        model_hash="ABC123MODELHASH",
        output_hash="OUTPUT123"
    )

    print("\n--- Verifying Ledger ---\n")

    verify_ledger()