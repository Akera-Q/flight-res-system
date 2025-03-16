import sqlite3
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Get the correct absolute path to the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Gets 'server/scripts'
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../app/database.db"))  # Moves up to 'server/app'

def fetch_data():
    print(f"📂 Using Database Path: {DB_PATH}")  # Debugging Step
    conn = sqlite3.connect(DB_PATH)  # ✅ Uses correct absolute path
    c = conn.cursor()
    c.execute('SELECT x, y FROM interactions WHERE event="click"')
    clicks = c.fetchall()
    conn.close()

    print(f"📊 Retrieved Click Data: {clicks}")  # ✅ Debugging Step
    return clicks


def generate_heatmap(clicks):
    heatmap_data = np.zeros((1000, 1000))  # Adjust size based on webpage

    for x, y in clicks:
        if 0 <= x < 1000 and 0 <= y < 1000:
            heatmap_data[int(999 - y), int(x)] += 1  # ✅ Fix Y-axis flip

    plt.figure(figsize=(10, 8))
    sns.heatmap(heatmap_data, cmap='YlGnBu', cbar=False)
    plt.title('Heatmap of Clicks')

    # Save the heatmap image in the static folder
    STATIC_PATH = os.path.abspath(os.path.join(BASE_DIR, "../static/heatmap.png"))
    print(f"📂 Saving Heatmap to: {STATIC_PATH}")  # Debugging step

    plt.savefig(STATIC_PATH)
    plt.close()


if __name__ == "__main__":
    clicks = fetch_data()
    generate_heatmap(clicks)
