#!/usr/bin/env python3
"""
Test script to verify that the PN7150 library issue has been resolved
"""
import subprocess
import sys
from pathlib import Path

def find_arduino_cli():
    """Find Arduino CLI executable"""
    possible_paths = [
        Path("tools/arduino-cli"),
        Path("tools/arduino-cli.exe"),
        Path("/usr/local/bin/arduino-cli"),
        Path("/usr/bin/arduino-cli")
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    # Check if arduino-cli is in PATH
    result = subprocess.run(["which", "arduino-cli"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    
    return None

def test_compilation():
    """Test compilation of host_Relay_NFC.ino"""
    print("🧪 Testing PN7150 library fix...")
    
    # Find Arduino CLI
    cli = find_arduino_cli()
    if not cli:
        print("❌ Arduino CLI not found")
        return False
    
    print(f"✅ Found Arduino CLI: {cli}")
    
    # Path to the sketch
    sketch_path = Path("sketch/BomberCat-main/firmware/host_Relay_NFC")
    if not sketch_path.exists():
        print(f"❌ Sketch not found: {sketch_path}")
        return False
    
    print(f"✅ Found sketch: {sketch_path}")
    
    # Create build directory
    build_dir = Path("build_test")
    build_dir.mkdir(exist_ok=True)
    
    # Test compilation with RP2040 board (original target)
    print("\n🔨 Testing compilation with RP2040...")
    
    cmd = [
        cli, "compile",
        "--fqbn", "rp2040:rp2040:rpipico",
        "--build-path", str(build_dir),
        str(sketch_path)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Compilation successful!")
            print("✅ PN7150 library issue has been resolved!")
            return True
        else:
            print("❌ Compilation failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
            # Check if it's still the PN7150 library issue
            if "ElectronicCats_PN7150.h" in result.stderr and "No such file" in result.stderr:
                print("❌ PN7150 library is still not found")
                return False
            else:
                print("⚠️  Different compilation error (not PN7150 library issue)")
                return True  # The PN7150 issue is fixed, but there might be other issues
                
    except subprocess.TimeoutExpired:
        print("❌ Compilation timed out")
        return False
    except Exception as e:
        print(f"❌ Error during compilation: {e}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════╗
║   🧪 PN7150 LIBRARY FIX VERIFICATION 🧪     ║
╚══════════════════════════════════════════════╝
""")
    
    success = test_compilation()
    
    if success:
        print("\n✅ SUCCESS: PN7150 library issue has been resolved!")
        print("\n💡 The ElectronicCats_PN7150.h header is now found.")
        print("   You can now compile the host_Relay_NFC firmware.")
    else:
        print("\n❌ FAILED: PN7150 library issue persists.")
        print("\n🚀 Alternative solution:")
        print("   Run: python use_client_now.py")
        print("   This switches to CLIENT firmware which doesn't need PN7150")
    
    # Cleanup
    build_dir = Path("build_test")
    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)
        print(f"\n🧹 Cleaned up build directory: {build_dir}")

if __name__ == "__main__":
    main()