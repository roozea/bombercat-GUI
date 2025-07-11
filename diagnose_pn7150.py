#!/usr/bin/env python3
"""
Quick diagnosis of PN7150 library issue
"""
import os
import subprocess
from pathlib import Path

def main():
    print("""
╔══════════════════════════════════════════════╗
║      🔍 PN7150 LIBRARY DIAGNOSTIC 🔍         ║
╚══════════════════════════════════════════════╝
""")
    
    # 1. Check Arduino libraries directory
    print("1. Checking Arduino libraries directory...")
    libs_paths = [
        Path.home() / "Documents" / "Arduino" / "libraries",
        Path.home() / "Library" / "Arduino15" / "libraries",  # macOS alternative
        Path.home() / "Arduino" / "libraries",
    ]
    
    arduino_libs = None
    for path in libs_paths:
        if path.exists():
            arduino_libs = path
            print(f"   ✅ Found: {path}")
            break
    
    if not arduino_libs:
        print("   ❌ Arduino libraries directory not found!")
        return
    
    # 2. Check for PN7150 library
    print("\n2. Looking for PN7150 library...")
    pn7150_found = False
    
    for item in arduino_libs.iterdir():
        if item.is_dir() and "pn7150" in item.name.lower():
            print(f"   ✅ Found: {item.name}")
            pn7150_found = True
            
            # Check contents
            headers = list(item.glob("*.h"))
            if headers:
                print(f"      Headers: {', '.join(h.name for h in headers[:3])}")
            
            # Check for src directory
            src_dir = item / "src"
            if src_dir.exists():
                src_headers = list(src_dir.glob("*.h"))
                if src_headers:
                    print(f"      Src headers: {', '.join(h.name for h in src_headers[:3])}")
    
    if not pn7150_found:
        print("   ❌ PN7150 library NOT FOUND!")
    
    # 3. Check current firmware
    print("\n3. Checking current firmware selection...")
    sketch_dir = Path("sketch")
    if sketch_dir.exists():
        # Check preference
        pref_file = sketch_dir / "relay_preference.txt"
        if pref_file.exists():
            pref = pref_file.read_text().strip()
            print(f"   Preference: {pref.upper()}")
        
        # Check downloaded firmware
        for fw_dir in sketch_dir.rglob("*Relay_NFC"):
            print(f"   Found firmware: {fw_dir.name}")
            
            # Check the .ino file
            ino_files = list(fw_dir.glob("*.ino"))
            if ino_files:
                with open(ino_files[0], 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if "ElectronicCats_PN7150.h" in content:
                        print(f"      ⚠️  Uses PN7150 library")
                    elif "Adafruit_PN532.h" in content:
                        print(f"      ✅ Uses PN532 library")
    
    # 4. Arduino CLI check
    print("\n4. Checking Arduino CLI...")
    cli_paths = ["tools/arduino-cli", "tools/arduino-cli.exe", "arduino-cli"]
    cli_found = False
    
    for cli in cli_paths:
        try:
            result = subprocess.run([cli, "version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Arduino CLI found: {cli}")
                cli_found = True
                
                # Check installed libraries
                result = subprocess.run([cli, "lib", "list"], capture_output=True, text=True)
                if "PN7150" in result.stdout:
                    print("   ✅ PN7150 listed in Arduino CLI")
                else:
                    print("   ❌ PN7150 NOT listed in Arduino CLI")
                break
        except:
            pass
    
    if not cli_found:
        print("   ❌ Arduino CLI not found")
    
    # DIAGNOSIS
    print("\n" + "="*50)
    print("DIAGNOSIS:")
    print("="*50)
    
    if not pn7150_found:
        print("\n❌ PROBLEM: PN7150 library is NOT installed")
        print("\n💡 SOLUTIONS:")
        print("1. Install the library:")
        print("   python fix_pn7150_library.py")
        print("\n2. Switch to CLIENT firmware (RECOMMENDED):")
        print("   python use_client_instead.py")
        print("\n3. Manual install:")
        print("   - Download: https://github.com/ElectronicCats/ElectronicCats-PN7150")
        print(f"   - Extract to: {arduino_libs}")
        print("   - Rename folder to: ElectronicCats_PN7150")
    else:
        print("\n✅ PN7150 library is installed")
        print("\n❓ But compilation still fails?")
        print("\nPossible issues:")
        print("1. Library name mismatch in include statement")
        print("2. Library not properly indexed by Arduino")
        print("3. Wrong library version")
        print("\n💡 Try:")
        print("1. python fix_pn7150_library.py")
        print("2. Or just use CLIENT: python use_client_instead.py")
    
    print("\n🚀 EASIEST SOLUTION: Just use CLIENT firmware!")
    print("It has the same functionality but better compatibility.")

if __name__ == "__main__":
    main()