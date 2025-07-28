#!/usr/bin/env python3
"""
Demo script for MP3 Lyrics Adder GUI

This script demonstrates how to run the GUI version of the MP3 Lyrics Adder.
Make sure you have all dependencies installed before running.
"""

import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        'tkinter',
        'mutagen', 
        'requests',
        'lyricsgenius',
        'python-dotenv'
    ]
    
    missing = []
    
    # Check tkinter (usually built-in)
    try:
        import tkinter
    except ImportError:
        missing.append('tkinter')
    
    # Check other modules
    for module in required_modules[1:]:
        try:
            __import__(module.replace('-', '_'))
        except ImportError:
            missing.append(module)
    
    if missing:
        print("❌ Missing dependencies:")
        for module in missing:
            print(f"   - {module}")
        print("\n📦 Install missing dependencies with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def main():
    """Main demo function"""
    print("🎵 MP3 Lyrics Adder GUI Demo")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    print("\n🚀 Starting GUI application...")
    
    # Import and run the GUI
    try:
        from lyrics_adder_gui import main as run_gui
        run_gui()
    except ImportError as e:
        print(f"❌ Error importing GUI module: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error running GUI: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())