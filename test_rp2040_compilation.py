#!/usr/bin/env python3

import subprocess
import sys
import os

def test_compilation():
    """Test compilation of the RP2040 firmware"""
    
    # Path to the firmware
    firmware_path = "sketch/BomberCat-main/firmware/host_Relay_NFC/host_Relay_NFC.ino"
    
    if not os.path.exists(firmware_path):
        print(f"Error: Firmware file not found at {firmware_path}")
        return False
    
    # Arduino CLI command for RP2040 compilation
    cmd = [
        "arduino-cli", "compile",
        "--fqbn", "rp2040:rp2040:rpipico",
        "--verbose",
        firmware_path
    ]
    
    print("Testing RP2040 compilation...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Compilation successful!")
            return True
        else:
            print("❌ Compilation failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Compilation timed out!")
        return False
    except FileNotFoundError:
        print("❌ arduino-cli not found. Please install Arduino CLI first.")
        return False
    except Exception as e:
        print(f"❌ Error during compilation: {e}")
        return False

if __name__ == "__main__":
    success = test_compilation()
    sys.exit(0 if success else 1)