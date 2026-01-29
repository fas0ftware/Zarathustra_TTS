import asyncio
import os
from voice_engine import VoiceEngine

async def main():
    # --- AYARLAR ---
    input_file = "script.txt"
    output_file = "part5.mp3"  # Çıktı dosyasının adı
    
    # 1. Dosya Kontrolü
    if not os.path.exists(input_file):
        print(f"UYARI: '{input_file}' bulunamadı. Lütfen oluşturun.")
        return

    # 2. Metni Oku (UTF-8 forma tında - Linux uyumlu)
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print("UYARI: script.txt dosyasının içi boş.")
        return

    # 3. Motoru Başlat
    # VoiceEngine dosyasında Ryan'ı varsayılan yaptık, burası boş kalsa da Ryan çalışır.
    engine = VoiceEngine() 
    
    print(f"📢 Okunan Metin: {text[:60]}...") 
    await engine.generate_audio(text, output_file)

if __name__ == "__main__":
    asyncio.run(main())