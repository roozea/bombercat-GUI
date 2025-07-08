#!/usr/bin/env python3
"""
BomberCat Complete Installation Script
Installs EVERYTHING including problematic libraries
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=True):
    """Run command and return result"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    return True

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
    
    if sys.platform != "win32":
        result = subprocess.run(["which", "arduino-cli"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    
    return None

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   🚀 BOMBERCAT COMPLETE INSTALLATION 🚀                 ║
╚══════════════════════════════════════════════════════════╝

This will install EVERYTHING including:
- All standard libraries
- Electronic Cats libraries
- Platform-specific libraries
- Alternative library names
""")
    
    cli = find_arduino_cli()
    if not cli:
        print("❌ Arduino CLI not found!")
        print("Run: python bombercat_relay.py")
        return 1
    
    print(f"✅ Found Arduino CLI: {cli}")
    
    # Add all board URLs
    print("\n📡 Adding board URLs...")
    urls = [
        "https://espressif.github.io/arduino-esp32/package_esp32_index.json",
        "https://electroniccats.github.io/Arduino_Boards_Index/package_electroniccats_index.json",
        "https://raw.githubusercontent.com/damellis/attiny/ide-1.6.x-boards-manager/package_damellis_attiny_index.json"
    ]
    
    for url in urls:
        run_command([cli, "config", "add", "board_manager.additional_urls", url], check=False)
    
    # Update index
    print("\n📥 Updating indexes...")
    run_command([cli, "core", "update-index"])
    
    # Install cores
    print("\n🎯 Installing cores...")
    cores = ["esp32:esp32", "arduino:avr"]
    
    for core in cores:
        print(f"Installing {core}...")
        run_command([cli, "core", "install", core], check=False)
    
    # Comprehensive library list
    all_libraries = [
        # Standard libraries
        "WiFiManager",
        "PubSubClient", 
        "ArduinoJson",
        "WiFiNINA",
        
        # NFC/RFID - Multiple variants
        "Adafruit PN532",
        "PN532",
        "RFID",
        "MFRC522",
        
        # Electronic Cats PN7150 - Try ALL variants
        "ElectronicCats-PN7150",
        "ElectronicCats PN7150",
        "Electronic Cats PN7150",
        "PN7150",
        "Electroniccats_PN7150",
        
        # NDEF variants
        "NDEF Library",
        "NDEF",
        "NDEF-1",
        "Seeed_Arduino_NFC_NDEF",
        "Don Coleman NDEF",
        
        # Serial Command variants
        "SerialCommand",
        "Arduino-SerialCommand",
        "SerialCommand-ng",
        "ppedro74 SerialCommand",
        
        # Servo variants
        "ESP32Servo",
        "ESP32_Servo",
        "ServoESP32",
        "Servo",
        
        # LED libraries
        "FastLED",
        "Adafruit NeoPixel",
        "WS2812FX",
        
        # Additional
        "Keyboard",
        "Mouse",
        "SD",
        "SPI",
        "Wire",
        
        # Storage (for mbed compatibility attempt)
        "SD_MMC",
        "SPIFFS",
        
        # Communication
        "HTTPClient",
        "WebServer",
        "ESPAsyncWebServer",
        "AsyncTCP"
    ]
    
    print(f"\n📚 Installing {len(all_libraries)} libraries...")
    print("This will take a while...\n")
    
    success = 0
    failed = []
    
    for i, lib in enumerate(all_libraries, 1):
        print(f"[{i}/{len(all_libraries)}] Installing: {lib}...", end=" ")
        
        result = subprocess.run(
            [cli, "lib", "install", lib],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅")
            success += 1
        else:
            print("❌")
            failed.append(lib)
    
    # Try git clone for failed Electronic Cats libraries
    if any("PN7150" in lib for lib in failed):
        print("\n🔧 Trying manual git clone for PN7150...")
        
        arduino_libs = Path.home() / "Documents" / "Arduino" / "libraries"
        arduino_libs.mkdir(parents=True, exist_ok=True)
        
        repos = [
            ("https://github.com/ElectronicCats/ElectronicCats-PN7150.git", "ElectronicCats-PN7150"),
            ("https://github.com/ElectronicCats/NDEF.git", "NDEF_ElectronicCats")
        ]
        
        for repo_url, folder_name in repos:
            target = arduino_libs / folder_name
            if not target.exists():
                print(f"Cloning {repo_url}...")
                result = subprocess.run(
                    ["git", "clone", repo_url, str(target)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✅ Cloned to {target}")
                    success += 1
                else:
                    print(f"❌ Failed to clone")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INSTALLATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully installed: {success} libraries")
    print(f"❌ Failed: {len(failed)} libraries")
    
    if failed:
        print("\n⚠️  Failed libraries (may be optional):")
        for lib in failed:
            if "PN7150" not in lib:  # Don't list PN7150 variants if we cloned it
                print(f"  • {lib}")
    
    # Final recommendations
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATIONS")
    print("=" * 60)
    
    print("\n1. If HOST firmware still fails:")
    print("   python switch_firmware_v2.py")
    print("   Select CLIENT (option 2)")
    
    print("\n2. To fix platform issues:")
    print("   python fix_platform_compatibility.py")
    
    print("\n3. Best practice:")
    print("   Use CLIENT firmware - it's more compatible!")
    
    print("\n✨ Installation complete!")
    print("Go to http://localhost:8081 and try again")

if __name__ == "__main__":
    sys.exit(main())