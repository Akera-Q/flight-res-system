import os
import sqlite3
import numpy as np
import scipy.ndimage
import seaborn as sns
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../app/database.db"))
STATIC_PATH = os.path.abspath(os.path.join(BASE_DIR, "../static/heatmap.png"))

def fetch_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT x, y FROM interactions WHERE event="click"')
    clicks = c.fetchall()
    conn.close()
    return clicks

def generate_heatmap(clicks):
    heatmap_width = 1920  
    heatmap_height = 1080  

    heatmap_data = np.zeros((heatmap_height, heatmap_width))

    # ✅ Vectorized update instead of nested loops
    for x, y in clicks:
        if 0 <= x < heatmap_width and 0 <= y < heatmap_height:
            heatmap_data[int(y), int(x)] += 1  # ✅ No manual flip

    # ✅ Apply Gaussian blur to spread heat smoothly (instead of loops)
    heatmap_data = scipy.ndimage.gaussian_filter(heatmap_data, sigma=5)

    plt.figure(figsize=(19.2, 10.8))
    sns.heatmap(heatmap_data, cmap='coolwarm', cbar=True) #add vmin=0, vmax=10 to make the scale way larger, but the colors will be less visible
    plt.savefig(STATIC_PATH)
    plt.close()

if __name__ == "__main__":
    clicks = fetch_data()
    generate_heatmap(clicks)

