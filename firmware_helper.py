#!/usr/bin/env python3
"""
BomberCat Firmware Helper
Quick guide for NFC Relay Attack setup
"""
import sys
import socket
from pathlib import Path

def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║      🔥 BOMBERCAT NFC RELAY GUIDE 🔥         ║
╚══════════════════════════════════════════════╝

For NFC Relay Attack, you need TWO BomberCat devices:

┌─────────────────────────────────────────────┐
│ 1️⃣  HOST Device (host_Relay_NFC)            │
│    📡 Connects to the legitimate NFC reader │
│    📍 Place near: ATM, door reader, terminal │
│    💡 Use Host Number: 1                    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 2️⃣  CLIENT Device (client_Relay_NFC)         │
│    📱 Emulates the NFC card                 │
│    📍 Place near: victim's wallet/card      │
│    💡 Use Host Number: 2                    │
└─────────────────────────────────────────────┘

════════════════════════════════════════════════
""")

def check_server_status():
    """Check if the BomberCat server is running"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8081))
    sock.close()
    return result == 0

def main():
    print_banner()
    
    print("📋 SETUP INSTRUCTIONS:")
    print("────────────────────────")
    print()
    print("1. Open the web interface: http://localhost:8081")
    print("2. Click 'START FLASH WIZARD'")
    print("3. Follow the wizard steps:")
    print("   - Connect your first BomberCat device")
    print("   - Install dependencies (automatic)")
    print("   - Configure WiFi and MQTT")
    print("   - SELECT THE ROLE (HOST or CLIENT) ← NEW!")
    print("   - Flash the firmware")
    print()
    print("4. Repeat for the second device with the other role")
    print()
    print("⚠️  IMPORTANT NOTES:")
    print("────────────────────")
    print("• Both devices must use the SAME WiFi network")
    print("• Both devices must use the SAME MQTT broker")
    print("• Use DIFFERENT Host Numbers (1 for HOST, 2 for CLIENT)")
    print("• The firmware selection is now done in the GUI!")
    print("• WiFiNINA library is automatically installed")
    print()
    
    # Check server status
    if check_server_status():
        print("✅ Server is running! Go to http://localhost:8081")
        print()
        print("🚀 Click here to open: http://localhost:8081")
    else:
        print("❌ Server not running. Start it with:")
        print("   python bombercat_relay.py")
        print()
        print("Then open: http://localhost:8081")
    
    print()
    print("💡 TIPS:")
    print("────────")
    print("• Test with MQTT Explorer to monitor messages")
    print("• Use a public broker for testing (broker.hivemq.com)")
    print("• For production, use your own MQTT broker")
    print("• Keep devices within WiFi range")
    print()
    print("Happy hacking! 🔥")

if __name__ == "__main__":
    main()