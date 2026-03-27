cat > README.md << 'EOF'
# 🎤 MIDI Live Player PRO

En professionel MIDI afspiller til live performance med avanceret mixer, pads, karaoke display og VU meters.

## ✨ Features

- 🎹 **12 Pads** - Konfigurbare MIDI triggers
- 🎛️ **16-kanal Mixer** - Full volume/mute/solo control
- 🎤 **Real-time Lyrics** - Karaoke display (36px font)
- 🎚️ **VU Meters** - Per-kanal level display (Grøn → Gul → Rød)
- 🌈 **6 Temaer** - Dark, Light, Midnight, Forest Green, Red Passion, Brown Wood, Ocean Blue
- ⏱️ **Tempo Control** - 0.25x - 2.0x playback speed
- 💾 **Session Save/Load** - Gem/indlæs dine setups
- 🎯 **Played Indicator** - ✓ Checkmark på afspillede pads
- 🔌 **MIDI Device Support** - Vælg output device

## 📋 Requirements

- Python 3.8+
- Windows, macOS eller Linux

## 🚀 Installation

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/midi-live-player.git
cd midi-live-player

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
🎮 Kontrol
Transport
▶ Play - Afspil valgt fil
⏸ Pause - Pause/resume
⏹ Stop - Stop playback
⏮ Prev / ⏭ Next - Navigate playlist
Mixer
Slider - Volume per kanal (0-127)
M - Mute kanal
S - Solo kanal
Master - Overall volume
Pads
Right-click - Load MIDI fil
Left-click - Play/stop pad
✓ Checkmark - Pad har været afspillet
Cyan border - Pad spiller nu
Playlist
Double-click - Afspil fil
Ctrl+O - Open MIDI fil
Ctrl+L - Add folder
🎨 Temaer
Vælg tema via View → Change Theme...:

Dark (default)
Light
Midnight
Forest Green
Red Passion
Brown Wood
Ocean Blue
💾 Save/Load
Session → Save... gemmer:

Hele playlist
Pad assignments
Tempo indstilling
Session → Load... gendanner dit setup

🎯 Workflow til Live Performance
Åbn app
File → Add Folder - Vælg din musikmappe
Assign pads med Right-click
Session → Save - Gem din setlist
Når du går live:
Afspil fra playlist med Play-knap
Trigger effekter/loops med pads
Adjust tempo med Tempo spinner
Monitor levels på VU meters
⌨️ Genveje
Ctrl+O - Open MIDI
Ctrl+S - Save Session
Ctrl+L - Load Session
Ctrl+Q - Exit
F5 - Refresh MIDI devices
Ctrl+, - Preferences
🔧 Preferences
Edit → Preferences:

Vælg MIDI output device
Automatisk husket
📝 Notes
Main musik + Pad: Når du trykker pad stopper main musikken
Pads er uafhængige: Kan bruge flere pads samtidig
Played indicator: Checkmark vises efter første afspilning
VU Meters: Grøn (lav) → Gul (medium) → Rød (høj)
Session save: Gem før performance!
🐛 Troubleshooting
Ingen MIDI output lyd?
Preferences → vælg device
Sørg for at device er tilsluttet
F5 for refresh devices
Pads virker ikke?
Right-click pad → Load MIDI
Sørg for fil er .mid eller .midi
VU Meters virker ikke?
Sørg for musik er indlæst med metadata
nogle MIDI filer har ikke velocity info
📄 License
MIT License - Se LICENSE fil

👨‍💻 Udviklet til
Live stage performance med:

Behringer FCB1010 controller support (fremtidig)
Akai APC Mini support (fremtidig)
Custom MIDI controller mapping (fremtidig)
