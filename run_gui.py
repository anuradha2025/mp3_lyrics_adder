#!/usr/bin/env python3
"""
Simple launcher for MP3 Lyrics Adder GUI

This script handles environment setup and launches the GUI application.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_virtual_env():
    """Check if we're in a virtual environment"""
    return hasattr(sys, 'prefix') and sys.prefix != sys.base_prefix

def activate_virtual_env():
    """Attempt to activate the virtual environment"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
        return False
    
    # Check if we're already in venv
    if check_virtual_env():
        return True
    
    print("🔧 Virtual environment found but not activated.")
    print("Please run: source venv/bin/activate")
    return False

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'tkinter', 'mutagen', 'requests', 'lyricsgenius', 'dotenv'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'dotenv':
                import dotenv
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    return True

def launch_gui():
    """Launch the GUI application"""
    try:
        print("🚀 Launching MP3 Lyrics Adder GUI...")
        
        # Import and run the GUI
        from lyrics_adder_gui import main as run_gui
        run_gui()
        
    except ImportError as e:
        print(f"❌ Failed to import GUI module: {e}")
        print("Please ensure all dependencies are installed and the GUI file exists.")
        return False
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🎵 MP3 Lyrics Adder - GUI Launcher")
    print("=" * 40)
    
    # Check virtual environment
    if not check_virtual_env():
        print("⚠️  Not running in virtual environment")
        if not activate_virtual_env():
            return 1
    else:
        print("✅ Running in virtual environment")
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    print("✅ All dependencies found")
    
    # Launch GUI
    if not launch_gui():
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)