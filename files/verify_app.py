#!/usr/bin/env python3
"""
Verification script for ShorterMusic application.
Tests that all modules can be imported and basic functionality works.
"""

import sys
from pathlib import Path

print("=" * 60)
print("ShorterMusic - Application Verification")
print("=" * 60)
print()

# Test 1: Python version check
print("1. Checking Python version...")
python_version = sys.version_info
print(f"   Python {python_version.major}.{python_version.minor}.{python_version.micro}")
if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
    print("   ✗ FAILED: Python 3.7+ required")
    sys.exit(1)
print("   ✓ OK")
print()

# Test 2: Import core modules
print("2. Testing core module imports...")
try:
    from App.core.app import ShorterMusicApp
    print("   ✓ ShorterMusicApp imported")
except ImportError as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

try:
    from App.utils.audio_loader import AudioLoader
    print("   ✓ AudioLoader imported")
except ImportError as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

try:
    from App.audio_analysis.segment_finder import SegmentFinder
    print("   ✓ SegmentFinder imported")
except ImportError as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

try:
    from App.mixing.transition_manager import TransitionManager
    print("   ✓ TransitionManager imported")
except ImportError as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

try:
    from App.youtube.playlist_downloader import PlaylistDownloader
    print("   ✓ PlaylistDownloader imported")
except ImportError as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

print()

# Test 3: Import dependencies
print("3. Testing required dependencies...")
required_packages = [
    'librosa',
    'soundfile',
    'numpy',
    'scipy',
    'pydub',
    'yt_dlp'
]

for package in required_packages:
    try:
        __import__(package)
        print(f"   ✓ {package}")
    except ImportError:
        print(f"   ✗ FAILED: {package} not installed")
        sys.exit(1)

print()

# Test 4: Initialize application
print("4. Testing application initialization...")
try:
    app = ShorterMusicApp()
    print("   ✓ ShorterMusicApp initialized")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 5: Check critical directories
print("5. Checking critical directories...")
critical_dirs = [
    'data',
    'data/output',
    'data/downloads',
    'App',
    'bin'
]

for dir_path in critical_dirs:
    path = Path(dir_path)
    if path.exists():
        print(f"   ✓ {dir_path} exists")
    else:
        print(f"   ! {dir_path} does not exist (will be created on demand)")

print()

# Test 6: Check bundled tools
print("6. Checking bundled external tools...")
bundled_tools = [
    'bin/ffmpeg',
    'bin/yt-dlp'
]

for tool_path in bundled_tools:
    path = Path(tool_path)
    if path.exists():
        print(f"   ✓ {tool_path} found")
    else:
        print(f"   ! {tool_path} not found (may use system version)")

print()

# Test 7: Test component initialization
print("7. Testing individual components...")
try:
    audio_loader = AudioLoader()
    print("   ✓ AudioLoader initialized")
except Exception as e:
    print(f"   ✗ AudioLoader failed: {e}")
    sys.exit(1)

try:
    segment_finder = SegmentFinder()
    print("   ✓ SegmentFinder initialized")
except Exception as e:
    print(f"   ✗ SegmentFinder failed: {e}")
    sys.exit(1)

try:
    transition_manager = TransitionManager()
    print("   ✓ TransitionManager initialized")
except Exception as e:
    print(f"   ✗ TransitionManager failed: {e}")
    sys.exit(1)

try:
    playlist_downloader = PlaylistDownloader()
    print("   ✓ PlaylistDownloader initialized")
except Exception as e:
    print(f"   ✗ PlaylistDownloader failed: {e}")
    sys.exit(1)

print()

# Test 8: Test directory creation
print("8. Testing directory creation...")
test_dir = Path("data/test_verify")
try:
    test_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✓ Created test directory: {test_dir}")

    # Clean up
    test_dir.rmdir()
    print(f"   ✓ Removed test directory")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

print()

# Final summary
print("=" * 60)
print("✓ ALL TESTS PASSED")
print("=" * 60)
print()
print("The ShorterMusic application is properly configured and ready to use.")
print()
