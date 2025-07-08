#!/usr/bin/env python3
"""
Automatically switch to CLIENT firmware
No questions asked - CLIENT just works better!
"""
from pathlib import Path

def main():
    print("""
╔══════════════════════════════════════════════╗
║   🚀 SWITCHING TO CLIENT FIRMWARE 🚀         ║
╚══════════════════════════════════════════════╝

CLIENT firmware is more compatible and works better!
""")
    
    # Create preference file
    sketch_dir = Path("sketch")
    sketch_dir.mkdir(exist_ok=True)
    
    preference_file = sketch_dir / "relay_preference.txt"
    preference_file.write_text("client")
    
    print("✅ Done! Now using CLIENT firmware")
    print()
    print("CLIENT firmware benefits:")
    print("  • Uses PN532 chip (widely supported)")
    print("  • No library compatibility issues")
    print("  • Same NFC relay functionality")
    print("  • Works great on ESP32")
    print()
    print("📋 Next steps:")
    print("1. Go back to http://localhost:8081")
    print("2. Click 'START FLASH WIZARD' again")
    print("3. It will now use CLIENT firmware automatically")
    print()
    print("💡 For NFC relay you need 2 devices:")
    print("  • Device 1 (CLIENT): Near victim's card")
    print("  • Device 2 (HOST): Near the reader")
    print()
    print("But CLIENT firmware is easier to get working first!")
    
    # Also create a marker to skip problematic libraries
    skip_libs = sketch_dir / "skip_problematic_libs.txt"
    skip_libs.write_text("PN7150")
    
    print("\n✨ All set! CLIENT firmware will be used.")

if __name__ == "__main__":
    main()