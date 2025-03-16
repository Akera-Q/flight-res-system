import sqlite3
import random

def insert_sample_data():
    conn = sqlite3.connect('server/app/database.db')  # Path to the SQLite DB
    c = conn.cursor()

    # Insert 100 sample click events with random coordinates
    for _ in range(100):  # Insert 100 sample clicks
        x = random.randint(0, 999)  # Random x coordinate between 0 and 999
        y = random.randint(0, 999)  # Random y coordinate between 0 and 999
        event = 'click'  # Event type, could be something else (coming up:scrolling {fire emoji!!!})
        c.execute('INSERT INTO interactions (x, y, event, scroll_top, scroll_height) VALUES (?, ?, ?, ?, ?)', 
          (x, y, event, None, None))

    conn.commit()
    conn.close()
    print("Sample data inserted successfully!")

if __name__ == "__main__":
    insert_sample_data()
