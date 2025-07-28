#!/usr/bin/env python3
"""
Test script for MP3 Lyrics Adder GUI
Tests basic functionality without requiring a display
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import tkinter
        print("✅ tkinter imported successfully")
    except ImportError as e:
        print(f"❌ tkinter import failed: {e}")
        return False
    
    try:
        import mutagen
        print("✅ mutagen imported successfully")
    except ImportError as e:
        print(f"❌ mutagen import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        import lyricsgenius
        print("✅ lyricsgenius imported successfully")
    except ImportError as e:
        print(f"❌ lyricsgenius import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    return True

def test_gui_class():
    """Test that the GUI class can be imported"""
    print("\n🧪 Testing GUI class import...")
    
    try:
        from lyrics_adder_gui import LyricsAdderGUI, GUILogHandler
        print("✅ LyricsAdderGUI class imported successfully")
        print("✅ GUILogHandler class imported successfully")
        return True
    except ImportError as e:
        print(f"❌ GUI class import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing GUI class: {e}")
        return False

def test_original_functionality():
    """Test that the original CLI functions still work"""
    print("\n🧪 Testing original CLI functionality...")
    
    try:
        from lyrics_adder import clean_lyrics, fetch_lyrics_ovh
        
        # Test lyrics cleaning function
        test_lyrics = """
        [Verse 1]
        Hello world
        This is a test
        
        [Chorus]
        Test lyrics here
        
        Contributors: Someone
        """
        
        cleaned = clean_lyrics(test_lyrics)
        if cleaned.strip():
            print("✅ Lyrics cleaning function works")
        else:
            print("❌ Lyrics cleaning function failed")
            return False
        
        print("✅ Original CLI functionality imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Original CLI import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing original functionality: {e}")
        return False

def main():
    """Run all tests"""
    print("🎵 MP3 Lyrics Adder GUI - Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Basic imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: GUI class import
    if test_gui_class():
        tests_passed += 1
    
    # Test 3: Original functionality
    if test_original_functionality():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The GUI application is ready to use.")
        print("\nTo run the GUI:")
        print("  python lyrics_adder_gui.py")
        print("  # or")
        print("  python demo_gui.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())