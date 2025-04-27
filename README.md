**MP3 Lyrics Adder**

A command‑line tool to automatically fetch and embed lyrics into your MP3 files’ ID3 tags. By default, it uses the free [lyrics.ovh](https://lyrics.ovh/) API, and if you supply a Genius API token, it will attempt Genius first and fall back to lyrics.ovh.

---

## 🔍 Features

- **Single File or Directory**: Pass a single `.mp3` file or a directory containing multiple MP3s—the tool will recurse through subfolders.
- **Automatic Lyrics Lookup**: Uses Genius (if API key provided) or lyrics.ovh as fallback.
- **Metadata‑driven**: Reads `TIT2` (Title), `TPE1` (Artist), `TALB` (Album) & `TPE2` (AlbumArtist).
- **Cleanup**: Strips headers, language markers (e.g. `eng||`), footers, and unwanted metadata.
- **Concurrency (Threads)**: Processes multiple files in parallel. Control via the `--threads` (`-j`) option.
- **.env Support**: Load `GENIUS_ACCESS_TOKEN` from `.env` (or environment) – sample `.env.example` provided.
- **PyInstaller‑bundled**: Distributed as a single `.exe` (no Python install required).

---

## 📋 Requirements

- Python 3.8+
- Windows, macOS, or Linux

Core dependencies (install via pip):

```txt
lyricsgenius==3.6.2
mutagen==1.47.0
requests==2.32.3
python-dotenv==1.1.0
```

If building the executable:

```txt
pyinstaller==6.13.0
pyinstaller-hooks-contrib==2025.3
```

> Note: Other dependencies (`urllib3`, `certifi`, etc.) are pulled in automatically.

---

## ⚙️ Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/anuradha2025/mp3‑lyrics‑adder.git
   cd mp3‑lyrics‑adder
   ```

2. **Create & activate** a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   .\venv\Scripts\activate # Windows
   ```

3. **Install** dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuration

1. **Copy** the sample environment file:

   ```bash
   cp .env.example .env
   ```

2. **Edit** `.env` and add your Genius API token:
   ```dotenv
   GENIUS_ACCESS_TOKEN=your_genius_token_here
   ```

If you leave `.env` blank or omit `GENIUS_ACCESS_TOKEN`, the tool defaults to lyrics.ovh only.

---

## 🚀 Usage

You can supply either a path to a single MP3 file or a directory of MP3s. The script will process every `.mp3` found in the folder (recursing into subdirectories).

```bash
# Process one file with lyrics.ovh only:
python lyrics_adder.py "/path/to/song.mp3"

# Process a directory recursively with 8 threads:
python lyrics_adder.py "~/Music" --threads 8

# Use Genius first (if token provided), then fallback to lyrics.ovh:
python lyrics_adder.py "~/Music" --token YOUR_TOKEN

# Overwrite existing lyrics tags on every file:
python lyrics_adder.py "~/Music" --overwrite

# View all options and help:
python lyrics_adder.py --help
```

---

## 📝 .env.example

```dotenv
# Rename to `.env` and add your Genius API token below
GENIUS_ACCESS_TOKEN=
```

---

## 🤝 Contributing

Contributions are welcome! Suggestions:

- Support additional lyric sources.
- Enhance cleanup heuristics.
- Add a GUI interface.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
