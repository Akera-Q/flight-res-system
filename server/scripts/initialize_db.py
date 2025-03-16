import sqlite3
import os

def create_db():
    # Get the correct absolute path for the database file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This gets 'server/scripts'
    DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../app/database.db"))  # Moves up to 'server/app'

    print(f"📂 Database Path: {DB_PATH}")  # Debugging step

    try:
        conn = sqlite3.connect(DB_PATH)  # Uses correct absolute path
        c = conn.cursor()

        # Create the interactions table if it doesn't exist
        c.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            event TEXT NOT NULL
        )
        ''')

        conn.commit()
        conn.close()
        print("✅ Database and table created successfully!")
    
    except sqlite3.OperationalError as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_db()
