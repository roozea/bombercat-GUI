#!/usr/bin/env python3
"""
Automatically switch to CLIENT firmware on ESP32
No questions asked - CLIENT just works better!
Now also sets the correct board type
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

def main():
    print("""
╔══════════════════════════════════════════════╗
║   🚀 SWITCHING TO CLIENT ON ESP32 🚀         ║
╚══════════════════════════════════════════════╝

CLIENT firmware is more compatible and works better!
Also fixing board type to ESP32...
""")
    
    # Create preference files
    sketch_dir = Path("sketch")
    sketch_dir.mkdir(exist_ok=True)
    
    # Set firmware preference to CLIENT
    preference_file = sketch_dir / "relay_preference.txt"
    preference_file.write_text("client")
    print("✅ Selected CLIENT firmware")
    
    # Set board preference to ESP32
    board_file = sketch_dir / "board_preference.txt"
    board_file.write_text("esp32:esp32:esp32")
    print("✅ Set board type to ESP32")
    
    # Try to install ESP32 core
    cli = find_arduino_cli()
    if cli:
        print("\n📦 Installing ESP32 core...")
        result = subprocess.run([cli, "core", "list"], capture_output=True, text=True)
        if "esp32:esp32" in result.stdout:
            print("✅ ESP32 core already installed")
        else:
            result = subprocess.run([cli, "core", "install", "esp32:esp32"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ ESP32 core installed successfully")
            else:
                print("⚠️  Could not install ESP32 core automatically")
                print("   You may need to install it via the wizard")
    
    print()
    print("✅ Done! Now using CLIENT firmware on ESP32")
    print()
    print("CLIENT firmware benefits:")
    print("  • Uses PN532 chip (widely supported)")
    print("  • No library compatibility issues")
    print("  • Same NFC relay functionality")
    print("  • Works great on ESP32")
    print("  • No platform-specific code")
    print()
    print("📋 Next steps:")
    print("1. Go back to http://localhost:8081")
    print("2. Click 'START FLASH WIZARD' again")
    print("3. It will now use CLIENT firmware on ESP32")
    print()
    print("💡 For NFC relay you need 2 devices:")
    print("  • Device 1 (CLIENT): Near victim's card")
    print("  • Device 2 (HOST): Near the reader")
    print()
    print("But CLIENT firmware is easier to get working first!")
    print()
    print("🔌 ESP32 Wiring for PN532:")
    print("  • SDA → GPIO 21")
    print("  • SCL → GPIO 22") 
    print("  • VCC → 3.3V (NOT 5V!)")
    print("  • GND → GND")
    
    # Also create a marker to skip problematic libraries
    skip_libs = sketch_dir / "skip_problematic_libs.txt"
    skip_libs.write_text("PN7150\nFlashIAPBlockDevice\nTDBStore\nmbed")
    
    print("\n✨ All set! CLIENT firmware on ESP32 will be used.")
    print("🚀 No more platform errors!")

if __name__ == "__main__":
    main()