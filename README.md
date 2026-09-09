# 🎙️ Talk-to-Write

**Talk-to-Write**, Linux (özellikle KDE Wayland) kullanıcıları için geliştirilmiş, **Wispr Flow** ve **SuperWhisper** alternatifi, ultra hızlı ve akıllı bir sesli dikte masaüstü asistanıdır.

Mikrofonunuzdan konuşmanızı dinler; konuşma dili dolgularını ("ııı", "şey", "yani", "falan") ve dilbilgisi hatalarını anında temizler. Aktif olan herhangi bir pencereye (kod editörü, tarayıcı, sohbet uygulamaları, terminal vb.) imleç odağını kaybetmeden doğrudan yazar.

---

## ✨ Temel Özellikler

- **Bas-Başlat / Bas-Bitir (Toggle Modu):** Tek bir kısayol tuşuyla (`Ctrl+Alt+Space`) kaydı başlatıp bitirin.
- **Odak Kaybetmeyen Yüzen Kapsül (Layer Shell Overlay):** Ekranın üstünde beliren, ses dalgası animasyonlu modern arayüz. Wayland Layer Shell protokolü sayesinde **yazdığınız pencerenin imleç odağını asla bozmaz**.
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

## 🛠️ Sistem Gereksinimleri ve Ön Koşullar

Uygulamanın Wayland üzerinde klavye tuş simülasyonu yapabilmesi, küresel kısayolları dinleyebilmesi ve arayüzü odak kaybetmeden çizebilmesi için sisteminizde birkaç temel paket bulunmalıdır.

### 1. Sistem Paketlerinin Kurulumu

Kullandığınız dağıtıma uygun komutla gerekli kütüphaneleri yükleyin:

#### **Fedora / RHEL:**
```bash
sudo dnf install wl-clipboard ydotool gtk4-layer-shell python3-gobject pipewire-utils portaudio-devel alsa-lib
```

#### **Ubuntu / Debian (22.04, 24.04+):**
```bash
sudo apt update
sudo apt install wl-clipboard ydotool libgtk4-layer-shell0 gir1.2-gtk4layershell-1.0 python3-gi python3-gi-cairo portaudio19-dev python3-pip python3-venv libasound2-dev
```

#### **Arch Linux / Manjaro:**
```bash
sudo pacman -S wl-clipboard ydotool gtk4-layer-shell python-gobject portaudio alsa-lib
```

---

### 2. Kritik İzinler ve `ydotool` Ayarı

`ydotool` ve `evdev`, Wayland altında küresel kısayol dinlemek ve aktif pencereye `Ctrl+V` yapıştırma simülasyonu göndermek için giriş aygıtı erişimine ihtiyaç duyar.

1. **Kullanıcınızı `input` grubuna ekleyin:**
   ```bash
   sudo usermod -aG input $USER
   ```
2. **`ydotool` arka plan servisini başlatın ve etkinleştirin:**
   ```bash
   systemctl --user enable --now ydotool
   ```
   *(Eğer dağıtımınızda user service tanımlı değilse, oturum açılışında arka planda `ydotoold &` çalıştırmanız yeterlidir).*

> [!IMPORTANT]
> Grup üyeliğinin (`input` grubu) sistemde aktif hale gelmesi için bu komutlardan sonra **oturumunuzu kapatıp yeniden açmanız (Log out / Log in)** veya bilgisayarınızı yeniden başlatmanız gerekir.

---

## 📥 Proje Kurulumu

### Adım 1: Depoyu Klonlayın
```bash
git clone https://github.com/<kullanici-adiniz>/talk-to-write.git
cd talk-to-write
```

### Adım 2: Python Sanal Ortamını Hazırlayın
Sistemdeki GTK4 Layer Shell kütüphanesini görebilmesi için sanal ortamı `--system-site-packages` parametresiyle oluşturun:

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

### Adım 3: Bağımlılıkları Yükleyin
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### Adım 4: Başlatıcı Betiğe Çalıştırma Yetkisi Verin
```bash
chmod +x bin/talk-to-write
```

---

## 🚀 Başlatma ve Kullanım

### 1. Uygulamayı Çalıştırma
```bash
./bin/talk-to-write
```
*(Arka planda sessizce çalıştırmak isterseniz: `./bin/talk-to-write &`)*

### 2. API Anahtarınızı Tanımlama
1. Ekranın sağ altındaki sistem çekmecesinde (System Tray) mor mikrofon ikonunu göreceksiniz.
2. İkona **sağ tıklayın** ve **⚙️ Ayarlar...** seçeneğini açın.
3. Tercihinize göre:
   - **Groq Cloud (Önerilen):** [console.groq.com](https://console.groq.com) adresinden alacağınız ücretsiz API anahtarını yapıştırın.
   - **Google Gemini:** Google AI Studio'dan aldığınız Gemini API anahtarını yapıştırın.
4. **Kaydet** butonuna basın.

*(Alternatif olarak terminalinizde `export GROQ_API_KEY="gsk_..."` veya `export GEMINI_API_KEY="AIzaSy..."` tanımlayabilirsiniz).*

### 3. Dikteyi Kullanma
1. Herhangi bir metin kutusuna (örneğin Kate, VS Code, tarayıcı arama kutusu vb.) tıklayın.
2. Klavyenizden **`Ctrl + Alt + Space`** tuşlarına basın.
   - Ekranın üstünde şık bir kapsül belirecek ve siz konuştukça dinleyecektir (yazı imleciniz kaybolmaz).
3. Cümlenizi söyleyin ve tekrar **`Ctrl + Alt + Space`** tuşuna basın.
4. 1 saniye içinde filtrelenmiş, dilbilgisi düzeltilmiş metin doğrudan imlecin olduğu yere yapıştırılacaktır!

---

## ⌨️ Özel Kısayol Tuşu Atama (KDE Plasma & GNOME)

Uygulama varsayılan olarak `Ctrl+Alt+Space` tuşlarını dinler. Ancak dilediğiniz herhangi bir tuşu (örneğin `Meta+Space`, `CapsLock`, `F8`) tetikleyici yapmak için sistem kısayollarını kullanabilirsiniz:

### **KDE Plasma:**
1. **Sistem Ayarları (System Settings)** -> **Kısayollar (Shortcuts)** bölümünü açın.
2. Alttan **"Yeni Ekle" -> "Komut"** seçin.
3. İsim: `Talk-to-Write Toggle`
4. Komut:
   ```bash
   /projenin/bulundugu/tam/yol/talk-to-write/bin/talk-to-write --toggle
   ```
5. İstediğiniz tuşu atayın ve **Uygula**'ya basın.

### **GNOME:**
1. **Ayarlar** -> **Klavye** -> **Kısayolları Görüntüle ve Özelleştir** -> **Özel Kısayollar**.
2. Yeni kısayol ekleyip komut olarak yukarıdaki `bin/talk-to-write --toggle` tam yolunu girin.

---

## 🧪 Testleri Çalıştırma

Kodların ve bağımlılıkların sisteminizde eksiksiz çalıştığını doğrulamak için birim testleri çalıştırabilirsiniz:

```bash
.venv/bin/pytest -v
```

---

## ❓ Sorun Giderme (FAQ)

- **Soru: Tuşa bastığımda metin yapıştırılmıyor.**
  - **Çözüm:** `ydotool` servisinin çalıştığından emin olun: `systemctl --user status ydotool`. Ayrıca kullanıcınızın `input` grubunda olduğunu `groups` komutuyla doğrulayın. Yeni eklendiyseniz oturumu kapatıp açmayı unutmayın.
- **Soru: Kapsül ekranda görünmüyor veya odağı bozuyor.**
  - **Çözüm:** `gtk4-layer-shell` paketinin sisteminizde kurulu olduğundan emin olun. Bu kütüphane Wayland üzerinde pencerenin klavye odağını çalmasını donanımsal olarak engeller.
- **Soru: Sesim çok kısık algılanıyor.**
  - **Çözüm:** Uygulama içerisinde otomatik kazanç artırımı (volume normalization) aktiftir, ancak KDE/GNOME Sistem Ses Ayarlarından mikrofon giriş seviyenizin en az %50 olduğundan emin olun.

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır. Katkıda bulunmaktan ve geliştirmekten çekinmeyin!
