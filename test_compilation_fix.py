#!/usr/bin/env python3

import subprocess
import sys
import os

def test_compilation():
    """Test if the Arduino sketch compiles without mbed errors"""
    
    sketch_path = "sketch/BomberCat-main/firmware/host_Relay_NFC/host_Relay_NFC.ino"
    
    if not os.path.exists(sketch_path):
        print(f"Error: Sketch file not found at {sketch_path}")
        return False
    
    print("Testing Arduino sketch compilation...")
    print(f"Sketch: {sketch_path}")
    
    # Try to run the existing compilation test
    try:
        result = subprocess.run([
            "python3", "test_final_compilation.py"
        ], capture_output=True, text=True, timeout=300)
        
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print(f"\nReturn code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Compilation test PASSED!")
            return True
        else:
            print("❌ Compilation test FAILED!")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Compilation test TIMED OUT!")
        return False
    except Exception as e:
        print(f"❌ Error running compilation test: {e}")
        return False

if __name__ == "__main__":
    success = test_compilation()
    sys.exit(0 if success else 1)