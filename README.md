# 🎙️ Talk-to-Write

**Talk-to-Write**, **Linux**, **Windows** ve **macOS** için geliştirilmiş, **Wispr Flow** ve **SuperWhisper** alternatifi, ultra hızlı ve akıllı bir sesli dikte masaüstü asistanıdır.

Mikrofonunuzdan konuşmanızı dinler; konuşma dili dolgularını ("ııı", "şey", "yani", "falan") ve dilbilgisi hatalarını anında temizler. Aktif olan herhangi bir pencereye (kod editörü, tarayıcı, Word, sohbet uygulamaları, terminal vb.) imleç odağını kaybetmeden doğrudan yazar.

---

## ✨ Temel Özellikler

- **Çapraz Platform Desteği:** Linux (KDE Wayland/GNOME/Hyprland), Windows (10/11) ve macOS (Apple Silicon & Intel).
- **Bas-Başlat / Bas-Bitir (Toggle Modu):** Tek bir kısayol tuşuyla (`Ctrl+Alt+Space`) kaydı başlatıp bitirin.
- **Odak Kaybetmeyen Yüzen Kapsül (Floating Pill):** Ekranın üstünde beliren, ses dalgası animasyonlu modern arayüz. Yazdığınız pencerenin **imleç odağını asla bozmaz**.
- **Otomatik Ses Normalizasyonu (Volume Boost):** Kısık sesli veya laptop mikrofonlarını otomatik olarak analiz eder ve en ideal seviyeye yükselterek yapay zekaya iletir.
- **Yapay Zeka Destekli Düzenleme:**
  - **Groq Cloud (Önerilen - Ultra Hızlı):** Whisper Large v3 Turbo (~200ms) + Llama/Qwen ile anında metin dökümü ve biçimlendirme.
  - **Google Gemini 2.0 Flash:** Çok modlu (multimodal) ses anlama ve doğrudan dikte.
- **5 Farklı Yazma Modu (Personas):**
  - ✍️ **Doğal Dikte (Varsayılan):** Anlamı birebir korur, dolguları atar, yazım ve noktalamayı düzeltir.
  - 💬 **Hızlı Mesajlaşma (Chat):** Slack, WhatsApp ve Discord için samimi, akıcı ve dolaysız mesaj dili.
  - ✉️ **Resmi E-Posta:** Kurumsal, nazik ve paragraflara ayrılmış e-posta metni.
  - 🤖 **AI Prompt Oluşturucu:** Dağınık sesli düşünceleri yapılandırılmış LLM istemine çevirir.
  - 📝 **Madde İmleri (Notlar):** Konuşulanları maddeler halinde özetler.
- **Özel Kelime Dağarcığı (Custom Vocabulary):** Sık kullandığınız teknik terimler, özel isimler veya kodlama kütüphanelerini tanımlayabilme.
- **Sistem Çekmecesi (System Tray):** Arka planda sessizce çalışır, mod değiştirmeyi ve ayarlara erişmeyi sağlar.
- **Akustik Geri Bildirim:** Kayıt başlama, bitiş, başarı ve hata durumlarında hafif, zarif ses tonları.

---

## 🛠️ İşletim Sistemine Göre Kurulum

<details open>
<summary><b>🐧 Linux Kurulumu (KDE Wayland / GNOME / X11)</b></summary>

### 1. Sistem Paketlerini Yükleyin
- **Fedora / RHEL:**
  ```bash
  sudo dnf install wl-clipboard ydotool gtk4-layer-shell python3-gobject pipewire-utils portaudio-devel alsa-lib
  ```
- **Ubuntu / Debian (22.04, 24.04+):**
  ```bash
  sudo apt update
  sudo apt install wl-clipboard ydotool libgtk4-layer-shell0 gir1.2-gtk4layershell-1.0 python3-gi python3-gi-cairo portaudio19-dev python3-pip python3-venv libasound2-dev
  ```
- **Arch Linux / Manjaro:**
  ```bash
  sudo pacman -S wl-clipboard ydotool gtk4-layer-shell python-gobject portaudio alsa-lib
  ```

### 2. İzinleri ve ydotool Servisini Ayarlayın
```bash
sudo usermod -aG input $USER
systemctl --user enable --now ydotool
```
*(Grup değişikliğinin geçerli olması için oturumu kapatıp yeniden açın).*

### 3. Tek Tıkla Kurulum ve Başlat Menüsüne Ekleme (Önerilen)
Depoyu klonlayıp tek komutla kurabilirsiniz:
```bash
git clone https://github.com/fat1h-ozturk/talk-to-write.git
cd talk-to-write
./install.sh
```
> Kurulum betiği sanal ortamı hazırlar, bağımlılıkları yükler ve Talk-to-Write'ı doğrudan **Başlat Menünüze (KDE Kickoff, GNOME Arama)** simgesiyle birlikte kaydeder.

*(Alternatif Manuel Kurulum)*:
```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m talk_to_write --install
```

### 4. Güncelleme Nasıl Yapılır?
Yeni bir sürüm yayınlandığında tek komutla güncellemek için:
```bash
./update.sh
```
veya manuel:
```bash
git pull
.venv/bin/pip install -r requirements.txt
```

### 5. Başlatın
- **Başlat Menüsü / KRunner:** Süper (Windows) tuşuna basıp `Talk-to-Write` veya `Dikte` yazarak açabilirsiniz.
- **Terminalden:** `./bin/talk-to-write`
</details>

<details>
<summary><b>🪟 Windows Kurulumu & Güncellenebilir Yapılandırma (Windows 10 / 11)</b></summary>

Windows üzerinde harici bir servis kurmanıza gerek **yoktur**; yerel Win32 API (`keybd_event` ve `OpenClipboard`) doğrudan kullanılır.

### 1. Ön Koşullar (Yalnızca İlk Kurulumda)
1. **Git for Windows**: Güncellemeleri alabilmek için [Git for Windows](https://git-scm.com/download/win) kurulu olmalıdır.
2. **Python 3.10 veya üzeri**: [python.org](https://www.python.org/downloads/) üzerinden indirip kurun.
   > [!IMPORTANT]
   > Python kurulum sihirbazının ilk ekranında yer alan **"Add python.exe to PATH"** kutucuğunu **kesinlikle işaretleyin**.

### 2. Klonlama ve Tek Tıkla Kurulum
Komut İstemi'ni (**CMD**) veya **PowerShell**'i açın:
```cmd
git clone https://github.com/fat1h-ozturk/talk-to-write.git
cd talk-to-write
install.bat
```

> [!NOTE]
> **Neden Doğrudan Güncellenebilir?**  
> `install.bat` sihirbazı, uygulamayı sanal ortama **`-e` (editable / düzenlenebilir)** modunda bağlar. Kod dosyaları kopyalanmaz, klonlanan bu klasöre canlı referans verilir. Başlat Menüsü'ne eklenen kısayol da doğrudan bu ortama bağlanır. Bu sayede klasördeki kod güncellendiğinde tüm Windows sisteminde anında güncellenmiş olur!

### 3. İleride Nasıl Güncellenir?
Projeye yeni bir özellik veya doğruluk iyileştirmesi geldiğinde iki yöntemle güncelleyebilirsiniz:

- **Yöntem 1 (Tek Tıkla - En Pratik):**  
  `talk-to-write` klasöründeki **`update.bat`** dosyasına çift tıklayın.
- **Yöntem 2 (Komut İstemi / Terminal):**
  ```cmd
  cd talk-to-write
  update.bat
  ```

**`update.bat` arka planda ne yapar?**
1. GitHub deposundan en güncel değişiklikleri çeker (`git pull`).
2. `.venv` ortamına yeni bir paket gereksinimi eklendiyse otomatik yükler (`pip install -r requirements.txt`).
3. Windows Başlat Menüsü ve masaüstü bağlantılarını yeniler.
4. Başarı bildirimini ekranda gösterir.

### 4. Başlatın
- **Windows Başlat Menüsü:** Klavyenizdeki Windows tuşuna basıp `Talk-to-Write` yazarak uygulamayı açabilirsiniz.
- **Komut Satırından:** `bin\talk-to-write.bat`
</details>

<details>
<summary><b>🍎 macOS Kurulumu (Apple Silicon M1/M2/M3/M4 & Intel)</b></summary>

macOS üzerinde ses çalma (`afplay`), pano (`pbcopy`) ve metin yapıştırma (AppleScript `Cmd+V`) işletim sisteminin yerel araçlarıyla çalışır.

### 1. Ön Koşul (PortAudio)
Homebrew yüklü değilse [brew.sh](https://brew.sh) üzerinden yükleyin, ardından:
```bash
brew install portaudio
```

### 2. Depoyu Klonlayın ve Bağımlılıkları Yükleyin
```bash
git clone https://github.com/fat1h-ozturk/talk-to-write.git
cd talk-to-write
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
chmod +x bin/talk-to-write
```

### 3. Başlatın ve İzinleri Verin
```bash
./bin/talk-to-write
```

> [!IMPORTANT]
> macOS güvenlik kuralları gereği, uygulamanın mikrofonu dinleyebilmesi ve aktif pencereye `Cmd+V` gönderebilmesi için **Sistem Ayarları -> Gizlilik ve Güvenlik** altından:
> 1. **Mikrofon (Microphone):** Terminal / Python için izin verin.
> 2. **Erişilebilirlik (Accessibility):** Terminal / Python için izin verin.

</details>

---

## 🚀 Kullanım Adımları

1. **API Anahtarını Girin:**
   - Uygulama açıldığında sağ alt (veya macOS'ta üst menü çubuğundaki) sistem çekmecesi ikonuna **sağ tıklayın** ve **⚙️ Ayarlar...** seçeneğini açın.
   - **Groq Cloud** (Önerilen, [console.groq.com](https://console.groq.com) üzerinden ücretsiz) veya **Google Gemini** API anahtarınızı girip **Kaydet**'e basın.
   *(İsteğe bağlı olarak terminalinizde `export GROQ_API_KEY="gsk_..."` veya Windows'ta `set GROQ_API_KEY=...` tanımlayabilirsiniz).*

2. **Dikteyi Başlatın:**
   - Herhangi bir uygulamadaki metin kutusuna (VS Code, Not Defteri, Word, tarayıcı, Slack vb.) tıklayın.
   - Klavyenizden **`Ctrl + Alt + Space`** tuşlarına basın.
   - Ekranın üstünde şık bir kapsül belirecek ve siz konuştukça dinleyecektir (yazı imleciniz kaybolmaz).
3. **Dikteyi Bitirin:**
   - Konuşmanız bittiğinde tekrar **`Ctrl + Alt + Space`** tuşlarına basın.
   - 1 saniye içinde filtrelenmiş, dilbilgisi düzeltilmiş metin doğrudan imlecin olduğu yere yapıştırılacaktır!

---

## ⌨️ Özel Kısayol Tuşu Entegrasyonu (`--toggle`)

Her işletim sisteminde `talk-to-write --toggle` komutu çalışır durumda olan uygulamayı anında tetikler:

- **Linux (KDE / GNOME):** Sistem Ayarları -> Kısayollar -> Yeni Komut: `talk-to-write --toggle`
- **Windows:** AutoHotkey veya Windows Görev Çubuğu kısayolu ile `bin\talk-to-write.bat --toggle`
- **macOS:** Kısayollar (Shortcuts) uygulaması veya Raycast / Alfred üzerinden `bin/talk-to-write --toggle`

---

## 🧪 Testleri Çalıştırma

Tüm platform adaptörlerini ve birim testleri doğrulamak için:

```bash
pytest -v
```

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır. Katkıda bulunmaktan ve geliştirmekten çekinmeyin!
