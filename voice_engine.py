import edge_tts

class VoiceEngine:
    # Varsayılan ses: Ryan (İngiliz Aksanı), Hız: Normal
    def __init__(self, voice="en-GB-RyanNeural", rate="+0%", pitch="+0Hz"):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch

    async def generate_audio(self, text, output_file):
        """
        Metni alır ve ses dosyasına çevirir.
        """
        try:
            print(f"⚙️  (Ryan) İşleniyor: {output_file}...")
            
            communicate = edge_tts.Communicate(
                text, 
                self.voice, 
                rate=self.rate, 
                pitch=self.pitch
            )
            
            await communicate.save(output_file)
            print(f"✅ Başarılı! Dosya kaydedildi: {output_file}")
            
        except Exception as e:
            print(f"❌ Hata oluştu: {e}")