#!/usr/bin/env python3
"""
Quick switch to CLIENT firmware
CLIENT is more compatible and doesn't need PN7150!
"""
from pathlib import Path
import sys

def main():
    print("""
╔══════════════════════════════════════════════╗
║   🚀 SWITCHING TO CLIENT FIRMWARE 🚀         ║
╚══════════════════════════════════════════════╝

CLIENT firmware is MUCH more compatible!

Why CLIENT is better:
  ✓ Uses PN532 chip (widely supported)
  ✓ No ElectronicCats_PN7150.h issues
  ✓ Same NFC relay functionality
  ✓ Better Arduino/ESP32 compatibility
  ✓ More examples and documentation

The only difference:
  • CLIENT: Place near victim's card
  • HOST: Place near the card reader
  
Both do the same relay attack!
""")
    
    # Create preference file
    sketch_dir = Path("sketch")
    sketch_dir.mkdir(exist_ok=True)
    
    preference_file = sketch_dir / "relay_preference.txt"
    preference_file.write_text("client")
    
    print("\n✅ Done! CLIENT firmware will be used")
    print("\n📋 Next steps:")
    print("1. Go back to the web interface")
    print("2. Click 'START FLASH WIZARD' again")
    print("3. It will now use CLIENT firmware")
    print("\n💡 Remember for CLIENT device:")
    print("  • Place it near the victim's NFC card")
    print("  • Use Host Number: 2")
    print("  • Connect to same WiFi/MQTT as HOST device")
    print("\n🔥 No more library errors!")
    
    # Also create a marker to skip PN7150
    skip_file = sketch_dir / "skip_pn7150.txt"
    skip_file.write_text("yes")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())