import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Gets 'server/scripts'
DB_PATH = os.path.join(BASE_DIR, "../app/database.db")  # Moves up to 'server/app'

print(f"📂 Database Path: {DB_PATH}")  # Debugging step

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interactions")
    rows = cursor.fetchall()

    if rows:
        print("✅ Data Found in Database:")
        for row in rows:
            print(row)
    else:
        print("❌ No Data Found. Make sure interactions are being recorded!")

    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
