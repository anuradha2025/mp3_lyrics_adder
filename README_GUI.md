# MP3 Lyrics Adder - GUI Version

A comprehensive graphical user interface for the MP3 Lyrics Adder tool, built with Python tkinter. This GUI provides an intuitive way to automatically fetch and embed lyrics into your MP3 files' ID3 tags.

![MP3 Lyrics Adder GUI](https://img.shields.io/badge/GUI-tkinter-blue.svg) ![Python](https://img.shields.io/badge/python-3.8+-green.svg) ![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## 🎵 Features

### Core Functionality
- **Intuitive GUI**: Modern, user-friendly interface built with tkinter
- **File & Directory Selection**: Easy browse buttons for selecting single files or entire directories
- **Dual API Support**: Uses Genius API (with token) or lyrics.ovh as fallback
- **Real-time Progress Tracking**: Progress bar, file counts, and live processing logs
- **Threaded Processing**: Non-blocking operation with configurable thread count
- **Smart Lyrics Cleanup**: Automatically removes headers, footers, and unwanted metadata

### GUI-Specific Features
- **Live Log Display**: Real-time processing messages in scrollable text area
- **Statistics Dashboard**: Live tracking of total, successful, and failed files
- **Progress Visualization**: Visual progress bar showing completion percentage
- **Configuration Management**: Built-in settings for API tokens and processing options
- **Environment Variable Support**: Automatically loads `.env` configuration
- **Stop/Resume Control**: Ability to stop processing mid-operation

## 📦 Installation

### Prerequisites
- Python 3.8+ with tkinter support
- Virtual environment (recommended)

### System Dependencies

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y python3-tk python3-venv
```

#### macOS
```bash
# tkinter is included with Python from python.org
# Or install via Homebrew:
brew install python-tk
```

#### Windows
```bash
# tkinter is included with standard Python installation
```

### Python Dependencies
1. **Clone the repository**
   ```bash
   git clone https://github.com/anuradha2025/mp3-lyrics-adder.git
   cd mp3-lyrics-adder
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Running the GUI
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Run the GUI application
python lyrics_adder_gui.py

# Or run the demo script
python demo_gui.py
```

### GUI Interface Guide

#### 1. File Selection
- **Select File**: Choose a single MP3 file to process
- **Select Directory**: Choose a directory containing MP3 files (processes recursively)
- **Path Display**: Shows the currently selected file or directory path

#### 2. Configuration
- **Use Genius API**: Toggle to enable/disable Genius API usage
- **Genius Token**: Enter your Genius API token (get one at [genius.com/api-clients](https://genius.com/api-clients))
- **Token Help**: Direct link to obtain your free API token

#### 3. Processing Options
- **Overwrite existing lyrics**: Check to replace existing lyrics in files
- **Concurrent threads**: Adjust the number of parallel processing threads (1-16)

#### 4. Controls
- **Start Processing**: Begin the lyrics fetching and embedding process
- **Stop**: Halt processing at any time
- **Clear Log**: Clear the processing log display

#### 5. Progress Monitoring
- **Progress Bar**: Visual representation of completion percentage
- **Statistics**: Real-time counts of total, successful, and failed files
- **Processing Log**: Detailed log messages with timestamps

### Environment Configuration

Create a `.env` file in the project directory:
```env
# Optional: Genius API token
GENIUS_ACCESS_TOKEN=your_genius_token_here
```

The GUI will automatically load this token on startup if available.

## 🔧 Configuration Options

### API Settings
- **Genius API**: Primary source for lyrics (requires free token)
- **lyrics.ovh**: Fallback API (no token required)
- **Automatic Fallback**: Uses lyrics.ovh when Genius fails or token not provided

### Processing Settings
- **Thread Count**: 1-16 concurrent threads (default: 4)
- **Overwrite Mode**: Replace existing lyrics or skip files with lyrics
- **Recursive Processing**: Automatically processes subdirectories

### Supported File Types
- **Input**: MP3 files with ID3 tags
- **Metadata Requirements**: Title (TIT2) and Artist (TPE1) tags must be present
- **Output**: Lyrics embedded as USLT (Unsynced Lyrics) tags

## 📋 Requirements

### Core Dependencies
```
lyricsgenius==3.6.2
mutagen==1.47.0
requests==2.32.3
python-dotenv==1.1.0
```

### System Requirements
- **Python**: 3.8 or higher
- **tkinter**: GUI framework (usually included with Python)
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimal requirements, scales with thread count
- **Storage**: No additional storage requirements

## 🛠️ Technical Details

### Architecture
- **GUI Framework**: tkinter with ttk styling
- **Threading**: Background processing with ThreadPoolExecutor
- **Logging**: Custom GUI log handler with queue-based messaging
- **Progress Tracking**: Real-time updates via thread-safe queues
- **Error Handling**: Graceful failure handling with user feedback

### File Processing Flow
1. **File Discovery**: Recursively find MP3 files in selected directory
2. **Metadata Extraction**: Read title and artist from ID3 tags
3. **Lyrics Fetching**: Query Genius API or lyrics.ovh
4. **Content Cleaning**: Remove unwanted headers and metadata
5. **Embedding**: Add cleaned lyrics as USLT tag
6. **Progress Updates**: Real-time status reporting to GUI

### Safety Features
- **Backup Recommendation**: Always backup your music library before processing
- **Non-Destructive**: Only adds lyrics tags, doesn't modify audio content
- **Error Recovery**: Continues processing other files if individual files fail
- **User Control**: Stop processing at any time with immediate response

## 🔍 Troubleshooting

### Common Issues

#### "No module named 'tkinter'"
```bash
# Linux
sudo apt install python3-tk

# macOS with Homebrew
brew install python-tk

# Windows - reinstall Python with tkinter option checked
```

#### "externally-managed-environment" Error
```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### GUI Not Responding
- Check that you're running in an environment with display support
- For SSH/remote access, use X11 forwarding: `ssh -X user@host`
- For headless servers, consider using the CLI version instead

#### No Lyrics Found
- Verify MP3 files have proper title and artist metadata
- Check internet connectivity for API access
- Try different API (toggle Genius/lyrics.ovh)
- Some songs may not be available in lyric databases

### Debug Mode
Enable detailed logging by modifying the log level in the GUI or checking the console output for additional error information.

## 🤝 Contributing

Contributions are welcome! Here are some areas for improvement:

### Potential Enhancements
- **Additional Lyrics Sources**: Support for more lyric APIs
- **Batch Configuration**: Save/load processing configurations
- **Dark Mode**: Theme support for better user experience
- **Lyrics Preview**: Preview lyrics before embedding
- **Undo Functionality**: Remove lyrics from files
- **Plugin System**: Extensible architecture for custom processors

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with the GUI
5. Submit a pull request

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Genius API**: For providing comprehensive lyrics database
- **lyrics.ovh**: For free lyrics API service
- **Python Community**: For excellent libraries (tkinter, mutagen, requests)
- **Contributors**: All those who help improve this tool

---

**Note**: This GUI version complements the command-line tool and provides the same core functionality with an enhanced user experience. Both versions can be used interchangeably depending on your preference and use case.