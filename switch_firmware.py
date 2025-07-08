#!/usr/bin/env python3
"""
BomberCat Firmware Switcher
Easily switch between different firmware options
"""
from pathlib import Path

def main():
    print("""
╔══════════════════════════════════════════════╗
║    🔄 BOMBERCAT FIRMWARE SWITCHER 🔄         ║
╚══════════════════════════════════════════════╝

If one firmware fails to compile, try another!
""")
    
    sketch_dir = Path("sketch")
    sketch_dir.mkdir(exist_ok=True)
    preference_file = sketch_dir / "relay_preference.txt"
    
    print("Available firmware options:")
    print("1. HOST - For NFC relay (connects to reader) [Uses PN7150]")
    print("2. CLIENT - For NFC relay (emulates card) [Uses PN532]")
    print("3. DETECT - Simple NFC tag detector [Minimal libs]")
    print("4. EXAMPLE - Built-in example firmware [Always works]")
    print()
    
    choice = input("Select firmware (1-4): ").strip()
    
    if choice == "1":
        preference_file.write_text("host")
        print("\n✅ Selected: HOST firmware")
        print("⚠️  Note: Requires ElectronicCats PN7150 library")
        print("If it fails, run: python fix_pn7150_library.py")
    elif choice == "2":
        preference_file.write_text("client")
        print("\n✅ Selected: CLIENT firmware")
        print("✅ This uses standard PN532 library (usually works)")
    elif choice == "3":
        preference_file.write_text("detect")
        print("\n✅ Selected: DETECT firmware")
        print("✅ Minimal dependencies, good for testing")
    elif choice == "4":
        preference_file.write_text("example")
        print("\n✅ Selected: EXAMPLE firmware")
        print("✅ Built-in firmware, guaranteed to compile")
    else:
        print("\n❌ Invalid choice")
        return
    
    print("\n📋 Next steps:")
    print("1. Go back to http://localhost:8081")
    print("2. Click 'START FLASH WIZARD'")
    print("3. The selected firmware will be used automatically")
    
    print("\n💡 Quick tips:")
    print("• If HOST fails → Try CLIENT (different libraries)")
    print("• If both fail → Use DETECT or EXAMPLE")
    print("• Install missing libs: python install_all_libraries_complete.py")

if __name__ == "__main__":
    main()