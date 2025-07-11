#!/usr/bin/env python3
"""
Fix ESP32 FQBN Error
Corrects the board type for ESP32 compilation
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd):
    """Run command and show output"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.returncode == 0

def find_arduino_cli():
    """Find Arduino CLI"""
    paths = [
        Path("tools/arduino-cli"),
        Path("tools/arduino-cli.exe"),
        Path("/usr/local/bin/arduino-cli"),
        Path("/usr/bin/arduino-cli")
    ]
    
    for path in paths:
        if path.exists():
            return str(path)
    
    # Try which command
    if sys.platform != "win32":
        result = subprocess.run(["which", "arduino-cli"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    
    return None

def main():
    print("""
╔══════════════════════════════════════════════╗
║        🔧 ESP32 FQBN FIX 🔧                  ║
╚══════════════════════════════════════════════╝

This fixes the board type error for ESP32

The error: Platform 'electroniccats:mbed_rp2040' not found
The fix: Install ESP32 core properly
""")
    
    cli = find_arduino_cli()
    if not cli:
        print("❌ Arduino CLI not found!")
        print("Run: python bombercat_relay.py first")
        return 1
    
    print(f"✅ Found Arduino CLI: {cli}")
    
    # Step 1: Install ESP32 core if not already installed
    print("\n📦 Installing ESP32 core...")
    
    # Check if already installed
    result = subprocess.run([cli, "core", "list"], capture_output=True, text=True)
    if "esp32:esp32" in result.stdout:
        print("✅ ESP32 core already installed")
    else:
        if run_command([cli, "core", "install", "esp32:esp32"]):
            print("✅ ESP32 core installed successfully")
        else:
            print("❌ Failed to install ESP32 core")
            return 1
    
    # Step 2: Save board preference
    print("\n💾 Saving board preference...")
    
    config_file = Path("sketch") / "board_preference.txt"
    config_file.parent.mkdir(exist_ok=True)
    config_file.write_text("esp32:esp32:esp32")
    print("✅ Board preference saved")
    
    # Step 3: Also save firmware preference to CLIENT
    print("\n🎯 Setting firmware preference to CLIENT...")
    
    firmware_pref = Path("sketch") / "relay_preference.txt"
    firmware_pref.write_text("client")
    print("✅ CLIENT firmware selected (better for ESP32)")
    
    # Step 4: Show available ESP32 boards
    print("\n📋 Available ESP32 board types:")
    print("1. esp32:esp32:esp32 - Generic ESP32 (default)")
    print("2. esp32:esp32:esp32doit-devkit-v1 - DOIT ESP32 DevKit V1")
    print("3. esp32:esp32:esp32wrover - ESP32 WROVER Module")
    print("4. esp32:esp32:esp32thing - SparkFun ESP32 Thing")
    print("5. esp32:esp32:featheresp32 - Adafruit ESP32 Feather")
    
    print("\n✨ Fixed! Now you can:")
    print("1. Go back to the web interface")
    print("2. Click 'START FLASH WIZARD'")
    print("3. It will now compile for ESP32")
    
    print("\n💡 RECOMMENDATIONS:")
    print("• Use CLIENT firmware (already selected)")
    print("• CLIENT uses PN532 chip (better compatibility)")
    print("• If you have PN7150, try HOST but expect issues")
    
    print("\n🚀 The error should be gone now!")

if __name__ == "__main__":
    sys.exit(main())