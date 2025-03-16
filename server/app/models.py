import sqlite3
import os

# Get absolute path to database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This gets 'server/app'
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../app/database.db"))  # This ensures correct path

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    x INTEGER,
                    y INTEGER,
                    scroll_top INTEGER,
                    scroll_height INTEGER
                )''')
    conn.commit()
    conn.close()

def insert_data(event, x=None, y=None, scroll_top=None, scroll_height=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO interactions (event, x, y, scroll_top, scroll_height)
                 VALUES (?, ?, ?, ?, ?)''', (event, x, y, scroll_top, scroll_height))
    conn.commit()
    conn.close()

# Call this function to initialize the database when the app starts
init_db()
