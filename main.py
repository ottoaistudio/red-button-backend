from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import os
import uuid
import time # Zaman takibi için eklendi

app = Flask(__name__)

DOWNLOAD_FOLDER = 'indirilenler'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# --- TEMİZLİK FONKSİYONU ---
def ortaligi_topla():
    """Klasördeki 10 dakikadan eski dosyaları siler."""
    try:
        su_an = time.time()
        süre_limiti = 600 # 600 saniye = 10 dakika
        
        files = os.listdir(DOWNLOAD_FOLDER)
        print(f"--- Temizlik Zamanı: {len(files)} dosya kontrol ediliyor ---")
        
        for dosya in files:
            dosya_yolu = os.path.join(DOWNLOAD_FOLDER, dosya)
            # Dosyanın oluşturulma zamanına bak
            if os.stat(dosya_yolu).st_mtime < su_an - süre_limiti:
                os.remove(dosya_yolu)
                print(f"🧹 Eski dosya silindi: {dosya}")
                
    except Exception as e:
        print(f"Temizlik hatası (Önemli değil): {e}")

@app.route('/coz', methods=['GET'])
def coz():
    # Her yeni istekte önce bir temizlik yapalım
    ortaligi_topla()

    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Link yok'})

    try:
        filename = f"{uuid.uuid4().hex}.mp4"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        print(f"Video indiriliyor... (Bu işlem videonun boyutuna göre sürer)")
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': filepath,
            'quiet': True,
            'nocheckcertificate': True, # Sertifika hatalarını yok say
            # Kendimizi Chrome tarayıcısı gibi tanıtıyoruz:
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        print("İndirme bitti, telefona servis ediliyor.")
        
        local_url = f"http://127.0.0.1:5000/dosya/{filename}"

        return jsonify({
            'status': 'success',
            'download_url': local_url
        })

    except Exception as e:
        print(f"Hata oluştu: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/dosya/<path:filename>')
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
