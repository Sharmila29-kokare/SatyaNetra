import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "ledger.db"


conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

cursor.execute("""
    UPDATE audit_ledger
    SET asset_name = 'TAMPERED_MODEL.pt'
    WHERE sequence_number = 1
""")

conn.commit()
conn.close()

print("⚠️ Test tampering performed.")
print("Run M3 verification now.")