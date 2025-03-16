from flask import request, jsonify, send_from_directory, current_app
from . import app
from .models import insert_data
import os
import subprocess


@app.route('/api/track', methods=['POST'])
def track():
    data = request.json
    event = data.get('event')
    x = data.get('x')
    y = data.get('y')
    scroll_top = data.get('scrollTop')
    scroll_height = data.get('scrollHeight')

    # ✅ Insert data first
    insert_data(event, x, y, scroll_top, scroll_height)

    # ✅ Now update the heatmap with the latest data
    subprocess.run(["python", "server/scripts/generate-heatmap.py"])

    return jsonify({"message": "Data received successfully"}), 200

def serve_static(filename):
    static_dir = os.path.abspath(os.path.join(current_app.root_path, "../static"))  # Adjusts path
    return send_from_directory(static_dir, filename)
