#!/usr/bin/env python3
"""
Test script to verify that the skip_problematic_libs.txt functionality works
"""
import sys
import os
from pathlib import Path

# Add current directory to path to import bombercat_relay
sys.path.insert(0, '.')

def test_skip_libraries_loading():
    """Test that skip libraries are loaded correctly"""
    print("🧪 Testing skip_problematic_libs.txt loading...")
    
    # Import the config
    from bombercat_relay import config
    
    # Check if PN7150 was added to incompatible libraries
    print(f"Incompatible libraries: {config.incompatible_libraries}")
    
    pn7150_found = any('PN7150' in lib for lib in config.incompatible_libraries)
    
    if pn7150_found:
        print("✅ PN7150 found in incompatible libraries list")
        return True
    else:
        print("❌ PN7150 not found in incompatible libraries list")
        return False

def test_firmware_processing():
    """Test that firmware processing comments out PN7150 includes"""
    print("\n🧪 Testing firmware processing...")
    
    # Create a test firmware file
    test_dir = Path("test_firmware")
    test_dir.mkdir(exist_ok=True)
    
    test_content = """
#include <SPI.h>
#include <WiFiNINA.h>
#include <ElectronicCats_PN7150.h>
#include <FlashIAPBlockDevice.h>
#include <TDBStore.h>

void setup() {
    Serial.begin(9600);
}

void loop() {
    // Test code
}
"""
    
    test_file = test_dir / "test_firmware.ino"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"Created test firmware: {test_file}")
    
    # Import and create firmware manager
    from bombercat_relay import FirmwareManager, arduino_cli, socketio
    
    # Create a mock firmware manager
    firmware_manager = FirmwareManager(arduino_cli, socketio)
    firmware_manager.sketch_path = test_dir
    
    # Process the firmware
    print("Processing firmware for compatibility...")
    firmware_manager.fix_firmware_compatibility()
    
    # Read the processed file
    with open(test_file, 'r') as f:
        processed_content = f.read()
    
    print("\nProcessed firmware content:")
    print("=" * 50)
    print(processed_content)
    print("=" * 50)
    
    # Check if PN7150 include was commented out
    pn7150_commented = "// #include <ElectronicCats_PN7150.h>" in processed_content
    flash_commented = "// #include <FlashIAPBlockDevice.h>" in processed_content
    tdb_commented = "// #include <TDBStore.h>" in processed_content
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    
    success = pn7150_commented and flash_commented and tdb_commented
    
    if success:
        print("✅ All problematic includes were commented out")
        return True
    else:
        print("❌ Some includes were not commented out:")
        print(f"   PN7150 commented: {pn7150_commented}")
        print(f"   FlashIAP commented: {flash_commented}")
        print(f"   TDBStore commented: {tdb_commented}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════╗
║   🧪 SKIP LIBRARIES FUNCTIONALITY TEST 🧪   ║
╚══════════════════════════════════════════════╝
""")
    
    # Test 1: Skip libraries loading
    test1_success = test_skip_libraries_loading()
    
    # Test 2: Firmware processing
    test2_success = test_firmware_processing()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"Skip libraries loading: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Firmware processing: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n✅ ALL TESTS PASSED!")
        print("\n💡 The skip_problematic_libs.txt functionality is working correctly.")
        print("   PN7150 and other problematic libraries will be commented out during compilation.")
        print("\n🚀 Now try compiling the firmware again - it should work!")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("\n🔧 The skip_problematic_libs.txt functionality needs debugging.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()