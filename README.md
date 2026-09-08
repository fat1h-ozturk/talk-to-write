# 🎙️ Talk-to-Write

**Talk-to-Write**, Linux (özellikle KDE Wayland) kullanıcıları için tasarlanmış, **Wispr Flow** ve **SuperWhisper** alternatifi, ultra hızlı bir sesli dikte ve akıllı metin dönüştürme masaüstü uygulamasıdır.

Mikrofonunuzdan konuşmanızı dinler; duraksamaları, dolgu kelimeleri ("ııı", "şey", "yani") ve dilbilgisi hatalarını anında temizler ve aktif olan herhangi bir uygulamaya (kod editörü, tarayıcı, Slack, terminal vb.) doğrudan yazar.

---

## ✨ Özellikler

- **Bas-Başlat / Bas-Bitir (Toggle Modu):** Tek bir kısayol tuşuyla kaydı başlatıp bitirin.
- **Dinamik Yüzen Kapsül (Floating Pill):** Ekranın üzerinde beliren, ses dalgası animasyonu ve canlı durum bildiren modern karanlık arayüz (sürükleyip dilediğiniz yere bırakabilirsiniz).
- **Yapay Zeka Destekli Düzenleme:**
  - **Google Gemini 2.0 Flash (Varsayılan):** Tek adımda çok modlu ses çözümleme ve akıllı temizleme.
  - **Groq Cloud Desteği:** Whisper Large v3 Turbo (~200ms STT) + Llama 3.3 70B ile biçimlendirme.
- **5 Farklı Yazma Modu (Personas):**
  1. ✍️ **Doğal Dikte (Varsayılan):** Anlamı birebir korur; dolgu kelimeleri atar, noktalama ve yazımı düzeltir.
  2. 💬 **Hızlı Mesajlaşma (Chat):** Slack, WhatsApp ve Discord için samimi, akıcı ve doğrudan mesaj dili.
  3. ✉️ **Resmi E-Posta:** Kurumsal ve nazik bir iş e-postası formatı.
  4. 🤖 **AI Prompt Oluşturucu:** Dağınık sesli düşünceleri yapılandırılmış bir LLM prompt'una dönüştürür.
  5. 📝 **Madde İmleri (Notlar):** Konuşulanları ana maddeler halinde özetler.
- **KDE Wayland Yerel Metin Enjeksiyonu:** `wl-copy` ve `ydotool` kullanarak aktif pencereye anında `Ctrl+V` simülasyonu yapar.
- **Sistem Çekmecesi (System Tray):** Arka planda sessizce çalışır, mod değiştirmeyi ve ayarlara erişmeyi sağlar.
- **Özel Kelime Dağarcığı:** Sık kullandığınız teknik terimler, özel isimler veya marka adlarını kolayca tanıtır.
- **Akustik Geri Bildirim:** Kayıt başlama, bitiş, başarı ve hata anlarında hafif, zarif ses tonları.

---

## 🚀 Hızlı Başlangıç

### 1. Uygulamayı Başlatma

Uygulamayı doğrudan terminalden veya oluşturulan script ile başlatabilirsiniz:

```bash
cd /home/fatih/projects/talk-to-write
./bin/talk-to-write
```

Arka planda başlatmak için:
```bash
./bin/talk-to-write &
```

### 2. API Anahtarını Tanımlama

Uygulama açıldığında sistem çekmecesindeki (sağ alt tepsi) **Talk-to-Write** ikonuna sağ tıklayıp **⚙️ Ayarlar**'ı seçin.
- **Google Gemini API Anahtarınızı** buraya yapıştırın ve **Kaydet**'e basın.
- *Alternatif olarak:* Terminalinizde `export GEMINI_API_KEY="AIzaSy..."` şeklinde ortam değişkeni olarak da tanımlayabilirsiniz.

---

## ⌨️ Kısayol Tuşu Entegrasyonu (KDE Plasma)

Uygulama varsayılan olarak dahili `Ctrl+Alt+Space` kombinasyonunu dinler. Ancak KDE Plasma Wayland üzerinde **herhangi bir özel tuşu (Örn: Meta+Space, CapsLock, F8 vb.)** tetikleyici yapmak için:

1. **KDE Sistem Ayarları (System Settings)** uygulamasını açın.
2. **Kısayollar (Shortcuts)** sekmesine gidin.
3. Alttaki **"Yeni Ekle" -> "Komut"** butonuna tıklayın.
4. İsim olarak `Talk-to-Write Toggle` yazın.
5. Komut kısmına şunu yazın:
   ```bash
   /home/fatih/projects/talk-to-write/bin/talk-to-write --toggle
   ```
6. Dilediğiniz tuş kombinasyonunu atayın ve **Uygula**'ya tıklayın.

Artık o tuşa her bastığınızda Talk-to-Write anında kayda başlar, tekrar bastığınızda metni yapıştırır!

---

## 🧪 Testleri Çalıştırma

Tüm birim testleri çalıştırmak için:

```bash
cd /home/fatih/projects/talk-to-write
.venv/bin/pytest -v
```

---

## 📁 Proje Yapısı

```
talk-to-write/
├── bin/
│   └── talk-to-write        # Başlatıcı kabuk betiği (CLI & Daemon)
├── talk_to_write/
│   ├── app.py               # Ana uygulama koordinatörü
│   ├── audio.py             # 16kHz mono ses kayıt motoru ve RMS seviyesi
│   ├── config.py            # JSON tabanlı ayar yöneticisi (~/.config/talk-to-write/)
│   ├── hotkey.py            # Evdev ve Unix IPC soket dinleyicisi
│   ├── injector.py          # Wayland wl-copy + ydotool metin enjektörü
│   ├── prompts.py           # Dikte, chat, email, prompt modları sistem şablonları
│   ├── sound.py             # Prosedürel akustik ton sentezleyici
│   ├── services/
│   │   ├── gemini.py        # Google Gemini 2.0 Flash çok modlu ses servisi
│   │   └── groq.py          # Groq Whisper STT + Llama 3 servisi
│   └── ui/
│       ├── pill.py          # Yüzen dinamik ada/kapsül arayüzü (Floating Pill)
│       ├── tray.py          # Sistem çekmecesi ikonu ve menüsü
│       └── settings.py      # Ayarlar penceresi
├── tests/                   # Kapsamlı birim testleri
├── pyproject.toml           # Paket tanımları
└── talk-to-write.desktop    # KDE Plasma masaüstü kısayolu
```
