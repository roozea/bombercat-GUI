#!/usr/bin/env python3
"""
BomberCat Bootloader Mode Detector
Detects when BomberCat is in BOOTSEL mode and ready to flash
"""
import os
import time
import platform
from pathlib import Path

def find_rpi_rp2_drive():
    """Find the RPI-RP2 drive (indicates BOOTSEL mode)"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # Check /Volumes
        volumes = Path("/Volumes")
        for volume in volumes.iterdir():
            if volume.name == "RPI-RP2":
                return str(volume)
    
    elif system == "Windows":
        # Check all drive letters
        import string
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                try:
                    # Check volume label
                    import subprocess
                    result = subprocess.run(
                        ["vol", f"{letter}:"],
                        capture_output=True,
                        text=True,
                        shell=True
                    )
                    if "RPI-RP2" in result.stdout:
                        return drive
                except:
                    pass
    
    elif system == "Linux":
        # Check /media and /mnt
        for base in ["/media", "/mnt"]:
            base_path = Path(base)
            if base_path.exists():
                for mount in base_path.rglob("RPI-RP2"):
                    return str(mount)
    
    return None

def is_bombercat_in_bootsel():
    """Check if BomberCat is in BOOTSEL mode"""
    return find_rpi_rp2_drive() is not None

def wait_for_bootsel_mode(timeout=30):
    """Wait for BomberCat to enter BOOTSEL mode"""
    print("Waiting for BomberCat to enter BOOTSEL mode...")
    print("Please:")
    print("1. Hold down the BOOTSEL button on BomberCat")
    print("2. Connect BomberCat to USB while holding BOOTSEL")
    print("3. Release the button after 2-3 seconds")
    print()
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if is_bombercat_in_bootsel():
            drive = find_rpi_rp2_drive()
            print(f"✅ BomberCat detected in BOOTSEL mode!")
            print(f"   Drive location: {drive}")
            return True
        
        # Animated waiting indicator
        remaining = timeout - int(time.time() - start_time)
        print(f"\r⏳ Waiting... {remaining}s remaining", end="", flush=True)
        time.sleep(0.5)
    
    print("\n❌ Timeout: BomberCat not detected in BOOTSEL mode")
    return False

def get_bootsel_instructions():
    """Get platform-specific instructions for entering BOOTSEL mode"""
    return """
╔══════════════════════════════════════════════════════╗
║     🔥 ENTERING BOMBERCAT BOOTSEL MODE 🔥           ║
╚══════════════════════════════════════════════════════╝

BomberCat uses RP2040 which requires BOOTSEL mode for flashing.

METHOD 1: BOOTSEL Button (Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Disconnect BomberCat from USB
2. Locate the BOOTSEL button (small button on the board)
3. Press and HOLD the BOOTSEL button
4. While holding BOOTSEL, connect USB cable
5. Keep holding for 2-3 seconds
6. Release the button
7. BomberCat should appear as "RPI-RP2" drive

METHOD 2: Double-Press Reset (If available)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
If your BomberCat has a RESET button:
1. Connect BomberCat to USB
2. Double-press the RESET button quickly
3. BomberCat should enter BOOTSEL mode

TROUBLESHOOTING:
━━━━━━━━━━━━━━
• No RPI-RP2 drive appears?
  - Try a different USB cable (data cable, not charging-only)
  - Try a different USB port
  - Hold BOOTSEL longer (up to 5 seconds)
  
• Already shows as a different drive?
  - That's CircuitPython mode, not BOOTSEL
  - You need to use Method 1 to enter BOOTSEL

• Board not responding?
  - Check USB cable is properly connected
  - Try USB 2.0 port instead of USB 3.0
  - On Linux: Check permissions (add user to dialout group)
"""

def main():
    print(get_bootsel_instructions())
    
    if is_bombercat_in_bootsel():
        drive = find_rpi_rp2_drive()
        print(f"\n✅ BomberCat is already in BOOTSEL mode!")
        print(f"   Drive location: {drive}")
    else:
        print("\n⚠️  BomberCat is NOT in BOOTSEL mode")
        print("\nWould you like to wait for it? (y/n): ", end="")
        
        response = input().strip().lower()
        if response == 'y':
            if wait_for_bootsel_mode(timeout=60):
                print("\n🎉 Success! BomberCat is ready for flashing")
            else:
                print("\n💡 Tips:")
                print("- Make sure you're using a data USB cable (not charge-only)")
                print("- Try a different USB port")
                print("- Hold BOOTSEL button BEFORE connecting USB")

if __name__ == "__main__":
    main()