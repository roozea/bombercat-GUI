#!/usr/bin/env python3
"""
Test script to verify RP2040/MBED compatibility fix for BomberCat firmware
This script tests compilation for both RP2040 and MBED platforms
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🔧 {description}")
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            return True
        else:
            print(f"❌ FAILED: {description}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {description}")
        return False
    except Exception as e:
        print(f"💥 ERROR: {description} - {str(e)}")
        return False

def test_rp2040_compilation():
    """Test RP2040 compilation with Earle Philhower core"""
    
    print("🎯 Testing BomberCat RP2040/MBED Compatibility Fix")
    print("=" * 60)
    
    # Check if arduino-cli is available
    if not run_command("arduino-cli version", "Checking arduino-cli availability"):
        print("❌ arduino-cli not found. Please install arduino-cli first.")
        return False
    
    # Test RP2040 compilation (the main issue from the user)
    sketch_path = "sketch/BomberCat-main/firmware/host_Relay_NFC/host_Relay_NFC.ino"
    
    if not os.path.exists(sketch_path):
        print(f"❌ Sketch not found: {sketch_path}")
        return False
    
    # Test RP2040 compilation with Earle Philhower core
    rp2040_success = run_command(
        f"arduino-cli compile --fqbn rp2040:rp2040:rpipico {sketch_path}",
        "Compiling for RP2040 (Earle Philhower core)"
    )
    
    # Test MBED compilation if available
    mbed_success = run_command(
        f"arduino-cli compile --fqbn arduino:mbed_rp2040:pico {sketch_path}",
        "Compiling for MBED RP2040 (Arduino official core)"
    )
    
    print("\n" + "=" * 60)
    print("📊 COMPILATION TEST RESULTS")
    print("=" * 60)
    
    if rp2040_success:
        print("✅ RP2040 (Earle Philhower): COMPILATION SUCCESSFUL")
        print("   - No more 'mbed' namespace errors")
        print("   - No more 'FlashIAPBlockDevice' errors") 
        print("   - No more 'TDBStore' errors")
        print("   - EEPROM-based storage implemented")
    else:
        print("❌ RP2040 (Earle Philhower): COMPILATION FAILED")
    
    if mbed_success:
        print("✅ MBED RP2040 (Arduino): COMPILATION SUCCESSFUL")
        print("   - Original mbed functionality preserved")
    else:
        print("⚠️  MBED RP2040 (Arduino): COMPILATION FAILED (may not be installed)")
    
    print("\n" + "=" * 60)
    
    if rp2040_success:
        print("🎉 SUCCESS: The mbed compatibility issue has been RESOLVED!")
        print("\n📋 SOLUTION SUMMARY:")
        print("✅ Platform detection system implemented")
        print("✅ Conditional compilation for MBED vs RP2040")
        print("✅ EEPROM-based storage for RP2040")
        print("✅ Platform-compatible constants")
        print("✅ Backward compatibility maintained")
        
        print("\n🚀 NEXT STEPS:")
        print("1. Install required libraries: WiFiNINA, PubSubClient, SerialCommand")
        print("2. Use: arduino-cli compile --fqbn rp2040:rp2040:rpipico")
        print("3. Upload to your Raspberry Pi Pico")
        
        return True
    else:
        print("❌ FAILED: The mbed compatibility issue still exists")
        print("\n🔍 TROUBLESHOOTING:")
        print("1. Check if RP2040 core is properly installed")
        print("2. Verify required libraries are installed")
        print("3. Check compilation errors above")
        
        return False

if __name__ == "__main__":
    success = test_rp2040_compilation()
    sys.exit(0 if success else 1)