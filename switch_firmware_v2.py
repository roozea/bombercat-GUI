#!/usr/bin/env python3
"""
BomberCat Firmware Selector v2 - WITH ESP32 FIX
Choose firmware and board type
"""
from pathlib import Path
import subprocess
import sys

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

def install_esp32_core(cli):
    """Install ESP32 core"""
    print("\n📦 Installing ESP32 core...")
    
    # Check if already installed
    result = subprocess.run([cli, "core", "list"], capture_output=True, text=True)
    if "esp32:esp32" in result.stdout:
        print("✅ ESP32 core already installed")
        return True
    
    # Install
    result = subprocess.run([cli, "core", "install", "esp32:esp32"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ ESP32 core installed successfully")
        return True
    else:
        print("❌ Failed to install ESP32 core")
        if result.stderr:
            print(result.stderr)
        return False

def main():
    print("""
╔══════════════════════════════════════════════╗
║      🔥 BOMBERCAT FIRMWARE SELECTOR V2 🔥     ║
╚══════════════════════════════════════════════╝

Select your firmware and board type:

1️⃣  HOST on ARM mbed (original BomberCat)
    • For Electronic Cats BomberCat RP2040
    • Uses PN7150 NFC chip
    
2️⃣  CLIENT on ESP32 (RECOMMENDED) ✨
    • For ESP32-based boards
    • Uses PN532 NFC chip
    • Better compatibility
    
3️⃣  AUTO DETECT
    • Let the system decide
    
4️⃣  EXAMPLE firmware (always works)
    • Simple NFC reader example
    • Works on any ESP32
    
5️⃣  FORCE CLIENT + ESP32 setup
    • Ensures everything is set for ESP32
    • Installs ESP32 core
    • Best for fixing errors

════════════════════════════════════════════════
""")
    
    choice = input("Enter your choice (1-5): ").strip()
    
    sketch_dir = Path("sketch")
    sketch_dir.mkdir(exist_ok=True)
    
    relay_pref_file = sketch_dir / "relay_preference.txt"
    board_pref_file = sketch_dir / "board_preference.txt"
    
    if choice == "1":
        # HOST on ARM mbed
        relay_pref_file.write_text("host")
        board_pref_file.write_text("electroniccats:mbed_rp2040:bombercat")
        print("\n✅ Selected: HOST firmware on ARM mbed")
        print("⚠️  Make sure you have the Electronic Cats board package installed!")
        
    elif choice == "2":
        # CLIENT on ESP32
        relay_pref_file.write_text("client")
        board_pref_file.write_text("esp32:esp32:esp32")
        print("\n✅ Selected: CLIENT firmware on ESP32")
        print("This is the recommended option!")
        
    elif choice == "3":
        # AUTO
        relay_pref_file.write_text("auto")
        if board_pref_file.exists():
            board_pref_file.unlink()
        print("\n✅ Selected: AUTO detection")
        
    elif choice == "4":
        # EXAMPLE
        relay_pref_file.write_text("example")
        board_pref_file.write_text("esp32:esp32:esp32")
        print("\n✅ Selected: EXAMPLE firmware on ESP32")
        print("This will create a simple working example")
        
    elif choice == "5":
        # FORCE CLIENT + ESP32
        print("\n🔧 Setting up ESP32 environment...")
        
        # Find Arduino CLI
        cli = find_arduino_cli()
        if cli:
            print(f"Found Arduino CLI: {cli}")
            install_esp32_core(cli)
        else:
            print("⚠️  Arduino CLI not found, but preferences will be saved")
        
        relay_pref_file.write_text("client")
        board_pref_file.write_text("esp32:esp32:esp32")
        
        print("\n✅ FORCED: CLIENT firmware on ESP32")
        print("✅ ESP32 core installed (if Arduino CLI found)")
        print("✅ All settings configured for ESP32")
        
    else:
        print("\n❌ Invalid choice")
        return
    
    print("\n" + "="*50)
    print("\n📋 Next Steps:")
    print("1. Go back to http://localhost:8081")
    print("2. Click 'START FLASH WIZARD'")
    print("3. The correct firmware and board will be used")
    
    if choice in ["2", "4", "5"]:
        print("\n💡 ESP32 Wiring Guide:")
        print("For PN532 (CLIENT firmware):")
        print("  • SDA → GPIO 21")
        print("  • SCL → GPIO 22")
        print("  • VCC → 3.3V (NOT 5V!)")
        print("  • GND → GND")
        print("  • IRQ → GPIO 2 (optional)")
        print("  • RST → GPIO 3 (optional)")
    
    print("\nHappy hacking! 🔥")

if __name__ == "__main__":
    main()