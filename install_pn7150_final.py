#!/usr/bin/env python3
"""
Final PN7150 Library Installer
Tries EVERYTHING to install this problematic library
"""
import subprocess
import os
import sys
import shutil
import requests
import zipfile
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return success status"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0 and result.stderr:
        print(f"Error: {result.stderr}")
    return result.returncode == 0

def main():
    print("""
╔══════════════════════════════════════════════╗
║   🔧 FINAL PN7150 INSTALLER 🔧               ║
╚══════════════════════════════════════════════╝

This will try EVERYTHING to install PN7150 library
""")
    
    # Find Arduino libraries directory
    arduino_libs = Path.home() / "Documents" / "Arduino" / "libraries"
    arduino_libs.mkdir(parents=True, exist_ok=True)
    
    print(f"Arduino libraries directory: {arduino_libs}")
    
    success = False
    
    # Method 1: Git clone
    print("\n📦 Method 1: Git clone from official repo...")
    
    target_names = [
        "ElectronicCats_PN7150",
        "ElectronicCats-PN7150", 
        "Electronic_Cats_PN7150"
    ]
    
    for target_name in target_names:
        target_path = arduino_libs / target_name
        if not target_path.exists():
            if run_command(["git", "clone", "https://github.com/ElectronicCats/ElectronicCats-PN7150.git", str(target_path)]):
                print(f"✅ Cloned to: {target_name}")
                success = True
                break
        else:
            print(f"⚠️  {target_name} already exists")
    
    # Method 2: Download ZIP
    if not success:
        print("\n📦 Method 2: Download ZIP from GitHub...")
        
        zip_url = "https://github.com/ElectronicCats/ElectronicCats-PN7150/archive/refs/heads/master.zip"
        zip_path = arduino_libs / "pn7150_temp.zip"
        
        try:
            print("Downloading...")
            response = requests.get(zip_url, timeout=30)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            print("Extracting...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(arduino_libs)
            
            # Rename extracted folder
            extracted = arduino_libs / "ElectronicCats-PN7150-master"
            if extracted.exists():
                for target_name in target_names:
                    target = arduino_libs / target_name
                    if not target.exists():
                        shutil.move(str(extracted), str(target))
                        print(f"✅ Installed as: {target_name}")
                        success = True
                        break
            
            # Clean up
            if zip_path.exists():
                zip_path.unlink()
                
        except Exception as e:
            print(f"❌ Download failed: {e}")
    
    # Method 3: Arduino CLI with different names
    if not success:
        print("\n📦 Method 3: Arduino CLI installation...")
        
        cli_path = None
        for path in ["tools/arduino-cli", "tools/arduino-cli.exe", "arduino-cli"]:
            if Path(path).exists() or shutil.which(path):
                cli_path = path
                break
        
        if cli_path:
            lib_names = [
                "ElectronicCats-PN7150",
                "ElectronicCats PN7150",
                "Electronic Cats PN7150",
                "PN7150"
            ]
            
            for lib_name in lib_names:
                if run_command([cli_path, "lib", "install", lib_name]):
                    print(f"✅ Installed via Arduino CLI: {lib_name}")
                    success = True
                    break
    
    # Method 4: Create compatibility links
    print("\n🔗 Creating compatibility links...")
    
    # Find any installed PN7150 library
    found_pn7150 = None
    for item in arduino_libs.iterdir():
        if item.is_dir() and "pn7150" in item.name.lower():
            found_pn7150 = item
            break
    
    if found_pn7150:
        print(f"Found PN7150 at: {found_pn7150.name}")
        
        # Create links/copies with different names
        link_names = [
            "ElectronicCats_PN7150",
            "ElectronicCatsPN7150",
            "Electroniccats_PN7150"
        ]
        
        for link_name in link_names:
            link_path = arduino_libs / link_name
            if not link_path.exists() and link_name != found_pn7150.name:
                try:
                    if sys.platform == "win32":
                        # Windows: copy
                        shutil.copytree(found_pn7150, link_path)
                        print(f"✅ Created copy: {link_name}")
                    else:
                        # Unix: symlink
                        os.symlink(found_pn7150, link_path)
                        print(f"✅ Created symlink: {link_name}")
                except Exception as e:
                    print(f"⚠️  Could not create {link_name}: {e}")
    
    # Final check
    print("\n📋 Checking installation...")
    pn7150_found = False
    
    for item in arduino_libs.iterdir():
        if item.is_dir() and "pn7150" in item.name.lower():
            print(f"✅ Found: {item.name}")
            pn7150_found = True
            
            # Check for header files
            headers = list(item.glob("*.h"))
            if headers:
                print(f"   Headers: {', '.join(h.name for h in headers[:3])}")
    
    if pn7150_found:
        print("\n✅ PN7150 library is installed!")
        print("\n💡 If compilation still fails, try:")
        print("1. Restart the Arduino IDE/CLI")
        print("2. Run: python fix_pn7150_include.py")
        print("3. Or better: Use CLIENT firmware instead!")
    else:
        print("\n❌ PN7150 installation failed!")
        print("\n🚀 STRONG RECOMMENDATION:")
        print("Just use CLIENT firmware instead!")
        print("\nRun: python use_client_now.py")
        print("\nCLIENT firmware:")
        print("  • Uses PN532 (not PN7150)")
        print("  • Much better compatibility")
        print("  • Same functionality")
        print("  • No library headaches!")

if __name__ == "__main__":
    main()