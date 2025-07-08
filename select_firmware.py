#!/usr/bin/env python3
"""
BomberCat Firmware Selector Helper
Helps you choose between HOST and CLIENT firmware for NFC relay
"""
from pathlib import Path
import sys

def main():
    print("""
╔══════════════════════════════════════════════╗
║      🔥 BOMBERCAT FIRMWARE SELECTOR 🔥        ║
╚══════════════════════════════════════════════╝

For NFC Relay Attack, you need TWO BomberCat devices:

1️⃣  HOST Device (host_Relay_NFC)
   📡 Connects to the legitimate NFC reader
   📍 Place near: ATM, door reader, payment terminal
   
2️⃣  CLIENT Device (client_Relay_NFC)  
   📱 Emulates the NFC card
   📍 Place near: victim's wallet/card

════════════════════════════════════════════════
""")
    
    print("Which device are you flashing right now?")
    print()
    print("1) HOST - This device will be near the card READER")
    print("2) CLIENT - This device will be near the victim's CARD")
    print("3) AUTO - Let the system decide (defaults to HOST)")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    sketch_dir = Path("sketch")
    sketch_dir.mkdir(exist_ok=True)
    preference_file = sketch_dir / "relay_preference.txt"
    
    if choice == "1":
        preference_file.write_text("host")
        print("\n✅ Selected: HOST firmware")
        print("This device will connect to the NFC reader")
        print("\nIMPORTANT:")
        print("- Place this device near the card reader")
        print("- Use Host Number: 1 (recommended)")
    elif choice == "2":
        preference_file.write_text("client")
        print("\n✅ Selected: CLIENT firmware")
        print("This device will emulate the NFC card")
        print("\nIMPORTANT:")
        print("- Place this device near the victim's card")
        print("- Use Host Number: 2 (recommended)")
    else:
        preference_file.write_text("auto")
        print("\n✅ Selected: AUTO (will use HOST by default)")
    
    print("\n" + "="*50)
    print("\n📋 Next Steps:")
    print("1. Go back to the wizard in your browser")
    print("2. Continue with the configuration")
    print("3. The correct firmware will be used automatically")
    print("\n💡 Remember:")
    print("- Both devices must use the SAME WiFi network")
    print("- Both devices must use the SAME MQTT broker")
    print("- Use different Host Numbers (1 for HOST, 2 for CLIENT)")
    print("\nHappy hacking! 🔥")

if __name__ == "__main__":
    main()