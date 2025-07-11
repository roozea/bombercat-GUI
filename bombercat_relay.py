#!/usr/bin/env python3
"""
BomberCat Arduino Flasher - Complete System with Arduino CLI Integration
Compiles and flashes firmware from ElectronicCats/BomberCat repository
Updated for RP2040 support with BOOTSEL detection
"""
import os
import sys
import json
import time
import shutil
import platform
import subprocess
import tempfile
import zipfile
import requests
import threading
import re
import string
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import serial
import serial.tools.list_ports

# Configuration
@dataclass
class Config:
    # Arduino CLI Settings
    arduino_cli_version: str = "0.35.3"
    arduino_cli_path: str = ""
    arduino_fqbn: str = "electroniccats:rp2040:bombercat"  # FQBN for BomberCat with Electronic Cats RP2040 core

    # BomberCat Repository
    repo_owner: str = "ElectronicCats"
    repo_name: str = "BomberCat"
    firmware_path: str = "firmware"

    # Build Settings
    build_dir: str = "build"
    sketch_dir: str = "sketch"

    # Board Manager URLs
    board_urls: List[str] = field(default_factory=lambda: [
        "https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json",
        "https://electroniccats.github.io/Arduino_Boards_Index/package_electroniccats_index.json"
    ])

    # Libraries to install
    required_libraries: List[str] = field(default_factory=lambda: [
        # Core Libraries
        "WiFiManager",
        "PubSubClient",
        "ArduinoJson",

        # NFC/RFID Libraries
        "Adafruit PN532",
        "ElectronicCats-PN7150",
        "NDEF Library",

        # Communication
        "WiFiNINA",
        "SerialCommand",

        # Hardware Control
        "Servo",
        "FastLED",
        "Adafruit NeoPixel",

        # Additional
        "Keyboard",
        "Mouse",
        "SD",
        "SPI",
        "Wire"
    ])

    # Alternative library names
    library_alternatives: Dict[str, List[str]] = field(default_factory=lambda: {
        "SerialCommand": ["Arduino-SerialCommand", "SerialCommand-ng"],
        "NDEF Library": ["NDEF", "NDEF-1", "Seeed_Arduino_NFC_NDEF"],
        "ElectronicCats-PN7150": ["ElectronicCats PN7150", "Electronic Cats PN7150", "PN7150"]
    })

    # Libraries that are platform-specific
    incompatible_libraries: List[str] = field(default_factory=lambda: [
        "FlashIAPBlockDevice.h",
        "TDBStore.h",
        "KVStore.h",
        "mbed.h",
        "rtos.h",
        "mbed_events.h"
    ])

    def load_skip_libraries(self):
        """Load additional libraries to skip from skip_problematic_libs.txt"""
        skip_file = Path("sketch/skip_problematic_libs.txt")
        if skip_file.exists():
            try:
                with open(skip_file, 'r') as f:
                    skip_libs = [line.strip() for line in f.readlines() if line.strip()]

                # Add .h extension if not present and convert to include format
                for lib in skip_libs:
                    if not lib.endswith('.h'):
                        lib_header = f"{lib}.h"
                    else:
                        lib_header = lib

                    if lib_header not in self.incompatible_libraries:
                        self.incompatible_libraries.append(lib_header)

                    # Also add the raw library name for broader matching
                    if lib not in self.incompatible_libraries:
                        self.incompatible_libraries.append(lib)

                print(f"Loaded {len(skip_libs)} additional libraries to skip: {skip_libs}")
                return True
            except Exception as e:
                print(f"Error loading skip_problematic_libs.txt: {e}")
        return False

    # Flask Settings
    flask_host: str = "0.0.0.0"
    flask_port: int = 8081
    flask_debug: bool = False

config = Config()

# Load additional libraries to skip from skip_problematic_libs.txt
config.load_skip_libraries()

# Create Flask app with SocketIO
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'bombercat-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=120, ping_interval=25)

# Global state for installation progress
installation_state = {
    "in_progress": False,
    "completed": False,
    "error": False,
    "message": ""
}

# Arduino CLI Manager
class ArduinoCLI:
    def __init__(self, socketio):
        self.socketio = socketio
        self.cli_path = None
        self.initialized = False

    def emit_log(self, message, level="info"):
        """Emit log message to web interface"""
        try:
            self.socketio.emit('flash_log', {
                'message': message,
                'level': level,
                'timestamp': time.strftime('%H:%M:%S')
            }, room=None)
            print(f"[{level.upper()}] {message}")
        except Exception as e:
            print(f"Error emitting log: {e}")

    def emit_progress(self, progress):
        """Emit progress update"""
        try:
            self.socketio.emit('flash_progress', {'progress': progress}, room=None)
        except Exception as e:
            print(f"Error emitting progress: {e}")

    def get_platform_info(self):
        """Get platform-specific Arduino CLI download info"""
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "windows":
            return "Windows_64bit", "arduino-cli.exe", ".zip"
        elif system == "darwin":
            if "arm" in machine:
                return "macOS_ARM64", "arduino-cli", ".tar.gz"
            else:
                return "macOS_64bit", "arduino-cli", ".tar.gz"
        elif system == "linux":
            if "arm" in machine:
                return "Linux_ARMv7", "arduino-cli", ".tar.gz"
            else:
                return "Linux_64bit", "arduino-cli", ".tar.gz"
        else:
            raise Exception(f"Unsupported platform: {system}")

    def download_arduino_cli(self):
        """Download and install Arduino CLI"""
        self.emit_log("Downloading Arduino CLI...")
        self.emit_progress(5)

        platform_name, exe_name, ext = self.get_platform_info()

        # Download URL
        base_url = "https://downloads.arduino.cc/arduino-cli"
        filename = f"arduino-cli_{config.arduino_cli_version}_{platform_name}{ext}"
        url = f"{base_url}/{filename}"

        # Download file
        response = requests.get(url, stream=True)
        response.raise_for_status()

        tools_dir = Path("tools")
        tools_dir.mkdir(exist_ok=True)

        archive_path = tools_dir / filename

        # Save archive
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(archive_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    progress = 5 + int((downloaded / total_size) * 10)
                    self.emit_progress(progress)

        # Extract archive
        self.emit_log("Extracting Arduino CLI...")

        if ext == ".zip":
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(tools_dir)
        else:  # tar.gz
            import tarfile
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(tools_dir)

        # Find arduino-cli executable
        self.cli_path = str(tools_dir / exe_name)

        # Make executable on Unix
        if platform.system() != "Windows":
            os.chmod(self.cli_path, 0o755)

        # Clean up archive
        archive_path.unlink()

        self.emit_log("Arduino CLI installed successfully", "success")
        self.emit_progress(15)

        return True

    def run_command(self, *args, **kwargs):
        """Run Arduino CLI command"""
        args = [str(arg) for arg in args if arg is not None]
        cmd = [self.cli_path] + args

        self.emit_log(f"Running: {' '.join(cmd)}", "info")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                **kwargs
            )

            is_board_list = "board" in args and "list" in args
            max_lines = 10 if is_board_list else 100

            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for i, line in enumerate(lines):
                    if i >= max_lines:
                        self.emit_log(f"... (truncated {len(lines) - max_lines} more lines)", "info")
                        break
                    if line:
                        self.emit_log(line, "info")

            if result.stderr:
                lines = result.stderr.strip().split('\n')
                for i, line in enumerate(lines):
                    if i >= max_lines:
                        self.emit_log(f"... (truncated {len(lines) - max_lines} more lines)", "warning")
                        break
                    if line:
                        self.emit_log(line, "warning")

            if result.returncode != 0:
                if "config init" in ' '.join(args) and "already exists" in result.stderr:
                    self.emit_log("Config already initialized", "info")
                    return result
                elif "already installed" in result.stderr:
                    self.emit_log("Component already installed", "info")
                    return result
                else:
                    error_msg = f"Command failed with code {result.returncode}"
                    if result.stderr:
                        error_msg += f": {result.stderr.strip()[:200]}"
                    raise Exception(error_msg)

            return result

        except Exception as e:
            self.emit_log(f"Command error: {str(e)}", "error")
            raise

    def initialize(self):
        """Initialize Arduino CLI"""
        if self.initialized:
            return True

        self.emit_log("Initializing Arduino CLI...")

        # Check if Arduino CLI exists
        if not self.cli_path or not os.path.exists(self.cli_path):
            self.download_arduino_cli()

        # Create Arduino CLI config directory
        home_dir = Path.home()
        arduino_dir = home_dir / ".arduino15"
        arduino_dir.mkdir(exist_ok=True)

        # Initialize configuration
        config_file = arduino_dir / "arduino-cli.yaml"
        if not config_file.exists():
            try:
                self.run_command("config", "init")
            except Exception as e:
                self.emit_log(f"Config init warning: {e}", "warning")
        else:
            self.emit_log("Arduino CLI config already exists", "info")

        # Add board manager URLs
        for url in config.board_urls:
            try:
                self.run_command("config", "add", "board_manager.additional_urls", url)
            except Exception as e:
                self.emit_log(f"Board URL already added or error: {e}", "warning")

        # Update core index
        self.emit_log("Updating board definitions...")
        self.emit_progress(20)
        try:
            self.run_command("core", "update-index")
        except Exception as e:
            self.emit_log(f"Core update warning: {e}", "warning")

        self.initialized = True
        return True

    def install_core(self, core_name="rp2040:rp2040"):
        """Install board core"""
        self.emit_log(f"Installing {core_name} core...")
        self.emit_progress(25)

        try:
            # Check if already installed
            result = self.run_command("core", "list")
            if core_name in result.stdout:
                self.emit_log(f"{core_name} core already installed", "success")
                self.emit_progress(35)
                return

            # Install the core
            self.run_command("core", "install", core_name)
            self.emit_log(f"{core_name} core installed", "success")
            self.emit_progress(35)
        except Exception as e:
            if "already installed" in str(e):
                self.emit_log(f"{core_name} core already installed", "success")
                self.emit_progress(35)
            else:
                self.emit_log(f"Core installation error: {e}", "error")
                raise

    def install_libraries(self):
        """Install required libraries"""
        self.emit_log("Installing required libraries...")
        self.emit_progress(40)

        total_libs = len(config.required_libraries)
        installed_count = 0
        failed_libs = []

        for i, lib in enumerate(config.required_libraries):
            self.emit_log(f"Installing library: {lib}")

            installed = False

            # Check if already installed
            try:
                result = self.run_command("lib", "list")
                if any(lib_part in result.stdout for lib_part in lib.split()):
                    self.emit_log(f"{lib} already installed", "info")
                    installed = True
                    installed_count += 1
            except:
                pass

            if not installed:
                # Try primary name
                try:
                    self.run_command("lib", "install", lib)
                    self.emit_log(f"{lib} installed", "success")
                    installed = True
                    installed_count += 1
                except Exception as e:
                    # Try alternative names
                    if lib in config.library_alternatives:
                        for alt_name in config.library_alternatives[lib]:
                            try:
                                self.emit_log(f"Trying alternative: {alt_name}")
                                self.run_command("lib", "install", alt_name)
                                self.emit_log(f"{lib} installed as {alt_name}", "success")
                                installed = True
                                installed_count += 1
                                break
                            except:
                                continue

                    if not installed:
                        self.emit_log(f"Warning: Failed to install {lib}: {e}", "warning")
                        failed_libs.append(lib)

            progress = 40 + int((i + 1) / total_libs * 10)
            self.emit_progress(progress)

        if failed_libs:
            self.emit_log(f"Installed {installed_count}/{total_libs} libraries", "warning")
            self.emit_log(f"Failed libraries: {', '.join(failed_libs)}", "warning")
        else:
            self.emit_log("All libraries installed successfully", "success")

        self.emit_progress(50)

    def detect_boards(self):
        """Detect connected boards"""
        self.emit_log("Detecting connected boards...")

        try:
            result = self.run_command("board", "list")

            bombercat_boards = []
            lines = result.stdout.strip().split('\n')

            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        port = parts[0]
                        if '/dev/' in port or 'COM' in port:
                            board_info = {
                                'port': port,
                                'fqbn': 'rp2040:rp2040:rpipico',
                                'name': 'RP2040 Device'
                            }

                            try:
                                if len(parts) > 4:
                                    name_parts = [p for p in parts[3:-2] if p is not None]
                                    if name_parts:
                                        board_info['name'] = ' '.join(name_parts)

                                    if 'rp2040' in line.lower() and len(parts) > 5:
                                        board_info['fqbn'] = parts[-2]
                            except Exception as e:
                                self.emit_log(f"Warning parsing board info: {e}", "warning")

                            bombercat_boards.append(board_info)

            if not bombercat_boards:
                self.emit_log("No boards detected via Arduino CLI, using serial port detection", "warning")

            return bombercat_boards

        except Exception as e:
            self.emit_log(f"Board detection error: {e}", "error")
            return []

# Firmware Manager
class FirmwareManager:
    def __init__(self, arduino_cli, socketio):
        self.arduino = arduino_cli
        self.socketio = socketio
        self.sketch_path = None

    def download_firmware(self):
        """Download firmware from GitHub"""
        self.arduino.emit_log("Downloading BomberCat firmware from GitHub...")
        self.arduino.emit_progress(55)

        sketch_dir = Path(config.sketch_dir)
        sketch_dir.mkdir(exist_ok=True)

        zip_url = f"https://github.com/{config.repo_owner}/{config.repo_name}/archive/refs/heads/main.zip"

        try:
            response = requests.get(zip_url, stream=True)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.arduino.emit_log(f"Error downloading firmware: {e}", "error")
            return self.create_example_firmware()

        zip_path = sketch_dir / "bombercat.zip"

        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        self.arduino.emit_log("Extracting firmware...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(sketch_dir)

        extracted_dir = sketch_dir / f"{config.repo_name}-main"
        firmware_dir = extracted_dir / "firmware"

        self.arduino.emit_log("Looking for firmware files...", "info")

        preference_file = sketch_dir / "relay_preference.txt"
        selected_firmware = None
        if preference_file.exists():
            selected_firmware = preference_file.read_text().strip().lower()

        available_firmwares = []
        if firmware_dir.exists():
            for subdir in firmware_dir.iterdir():
                if subdir.is_dir():
                    ino_files = list(subdir.glob("*.ino"))
                    if ino_files:
                        available_firmwares.append({
                            'name': subdir.name,
                            'path': subdir,
                            'ino_file': ino_files[0].name
                        })
                        self.arduino.emit_log(f"Found firmware: {subdir.name}/{ino_files[0].name}", "info")

        if not available_firmwares:
            self.arduino.emit_log("Searching for .ino files in entire repository...", "info")
            for ino_file in extracted_dir.rglob("*.ino"):
                if 'examples' not in str(ino_file).lower() and 'test' not in str(ino_file).lower():
                    available_firmwares.append({
                        'name': ino_file.parent.name,
                        'path': ino_file.parent,
                        'ino_file': ino_file.name
                    })
                    self.arduino.emit_log(f"Found: {ino_file.parent.name}/{ino_file.name}", "info")

        self.sketch_path = None

        host_relay = None
        client_relay = None

        for fw in available_firmwares:
            if 'host_relay_nfc' in fw['name'].lower():
                host_relay = fw
            elif 'client_relay_nfc' in fw['name'].lower():
                client_relay = fw

        if host_relay and client_relay:
            self.arduino.emit_log("Found both HOST and CLIENT relay firmwares!", "info")

            if selected_firmware == "host":
                self.sketch_path = host_relay['path']
                self.arduino.emit_log(f"Selected HOST firmware: {host_relay['name']}", "success")
            elif selected_firmware == "client":
                self.sketch_path = client_relay['path']
                self.arduino.emit_log(f"Selected CLIENT firmware: {client_relay['name']}", "success")
            else:
                self.sketch_path = host_relay['path']
                self.arduino.emit_log(f"Selected HOST firmware by default: {host_relay['name']}", "success")
        else:
            priority_names = ['host_relay_nfc', 'client_relay_nfc', 'DetectTags', 'BomberCat', 'Master', 'MasterReader', 'Reader', 'Main']

            for priority in priority_names:
                for fw in available_firmwares:
                    if priority.lower() in fw['name'].lower():
                        self.sketch_path = fw['path']
                        self.arduino.emit_log(f"Selected firmware: {fw['name']}", "success")
                        break
                if self.sketch_path:
                    break

        if not self.sketch_path and available_firmwares:
            self.sketch_path = available_firmwares[0]['path']
            self.arduino.emit_log(f"Selected firmware: {available_firmwares[0]['name']}", "success")

        zip_path.unlink()

        if not self.sketch_path:
            self.arduino.emit_log("No firmware found in repository, creating example", "warning")
            return self.create_example_firmware()

        self.fix_firmware_compatibility()

        self.arduino.emit_log("Firmware downloaded successfully", "success")
        self.arduino.emit_progress(60)

        return str(self.sketch_path)

    def fix_firmware_compatibility(self):
        """Fix library includes and platform-specific code"""
        if not self.sketch_path:
            return

        library_fixes = {
            '"ElectronicCats_PN7150.h"': '<ElectronicCats_PN7150.h>',
            '"Electroniccats_PN7150.h"': '<ElectronicCats_PN7150.h>',
            '"PN7150.h"': '<ElectronicCats_PN7150.h>',
            'Electroniccats_PN7150.h': 'ElectronicCats_PN7150.h'
        }

        arduino_libs = Path.home() / "Documents" / "Arduino" / "libraries"
        pn7150_found = None

        if arduino_libs.exists():
            for item in arduino_libs.iterdir():
                if item.is_dir() and "pn7150" in item.name.lower():
                    headers = list(item.glob("*.h"))
                    for header in headers:
                        if "pn7150" in header.name.lower():
                            pn7150_found = header.name
                            self.arduino.emit_log(f"Found PN7150 library: {item.name} with header: {header.name}", "info")
                            break

        if pn7150_found:
            for key in list(library_fixes.keys()):
                if "PN7150" in key:
                    library_fixes[key] = pn7150_found

        for ext in ['*.ino', '*.h', '*.cpp']:
            for file_path in Path(self.sketch_path).glob(ext):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    original_content = content
                    modified = False

                    for old_name, new_name in library_fixes.items():
                        if old_name in content:
                            content = content.replace(old_name, new_name)
                            modified = True
                            self.arduino.emit_log(f"Fixed include: {old_name} -> {new_name} in {file_path.name}", "info")

                    lines = content.split('\n')
                    new_lines = []

                    for line in lines:
                        if '#include "' in line and any(lib in line for lib in ['PN7150', 'ElectronicCats']):
                            match = re.search(r'#include\s*"([^"]+)"', line)
                            if match:
                                header = match.group(1)
                                for old, new in library_fixes.items():
                                    if old in header:
                                        header = new
                                new_line = f'#include <{header}>'
                                new_lines.append(new_line)
                                if new_line != line:
                                    self.arduino.emit_log(f"Changed include format: {line.strip()} -> {new_line}", "info")
                                    modified = True
                                continue

                        should_comment = False
                        for incompatible in config.incompatible_libraries:
                            # Check for exact matches
                            if f'#include <{incompatible}>' in line or f'#include "{incompatible}"' in line:
                                should_comment = True
                                self.arduino.emit_log(f"Commenting out incompatible include: {incompatible} in {file_path.name}", "warning")
                                break
                            # Check for partial matches (e.g., PN7150 matches ElectronicCats_PN7150.h)
                            elif incompatible in line and ('#include <' in line or '#include "' in line):
                                should_comment = True
                                self.arduino.emit_log(f"Commenting out incompatible include (partial match): {incompatible} in {file_path.name}", "warning")
                                break

                        if should_comment and not line.strip().startswith('//'):
                            new_lines.append(f"// {line} // Commented out - incompatible with RP2040")
                            modified = True
                        else:
                            new_lines.append(line)

                    if modified:
                        content = '\n'.join(new_lines)

                        if '#ifdef ARDUINO_ARCH_RP2040' not in content and any(inc in original_content for inc in config.incompatible_libraries):
                            defines = """
// Platform compatibility defines
#ifdef ARDUINO_ARCH_RP2040
  #define BOMBERCAT_RP2040
#endif

#ifdef ARDUINO_ARCH_MBED
  #define BOMBERCAT_MBED
#endif

"""
                            insert_pos = 0
                            for i, line in enumerate(new_lines):
                                if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('/*'):
                                    insert_pos = i
                                    break

                            new_lines.insert(insert_pos, defines)
                            content = '\n'.join(new_lines)
                            self.arduino.emit_log(f"Added platform compatibility defines to {file_path.name}", "info")

                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)

                except Exception as e:
                    self.arduino.emit_log(f"Warning: Could not process {file_path.name}: {e}", "warning")

    def create_example_firmware(self):
        """Create example BomberCat firmware for RP2040"""
        self.arduino.emit_log("Creating example BomberCat firmware...", "info")

        sketch_dir = Path(config.sketch_dir) / "BomberCat"
        sketch_dir.mkdir(parents=True, exist_ok=True)

        sketch_content = """
// BomberCat NFC Example for RP2040
// Compatible with Raspberry Pi Pico and similar boards

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

// Pin definitions for PN532 using I2C
#define PN532_IRQ   (2)
#define PN532_RESET (3)  

// Use I2C communication
Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);

// Include configuration
#include "bombercat_config.h"

// WiFi and MQTT clients
WiFiClient espClient;
PubSubClient mqtt(espClient);

// LED Pin (built-in LED on Pico)
#define LED_PIN 25

// NFC Variables
uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };
uint8_t uidLength;
unsigned long lastNFCRead = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 5000) delay(10);

  Serial.println("===================================");
  Serial.println("BomberCat NFC Example Starting...");
  Serial.println("Running on RP2040");
  Serial.println("===================================");

  // Initialize LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Connect to WiFi
  connectWiFi();

  // Setup MQTT
  mqtt.setServer(MQTT_SERVER, MQTT_PORT);
  mqtt.setCallback(mqttCallback);

  // Initialize NFC
  Serial.println("Initializing NFC module...");
  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.println("ERROR: Didn't find PN53x board");
    Serial.println("Check wiring:");
    Serial.println("- SDA to GPIO 4 (Pin 6)");
    Serial.println("- SCL to GPIO 5 (Pin 7)");
    Serial.println("- VCC to 3.3V");
    Serial.println("- GND to GND");
    while (1) {
      digitalWrite(LED_PIN, HIGH);
      delay(100);
      digitalWrite(LED_PIN, LOW);
      delay(100);
    }
  }

  Serial.print("Found chip PN5"); 
  Serial.println((versiondata>>24) & 0xFF, HEX);
  Serial.print("Firmware ver. "); 
  Serial.print((versiondata>>16) & 0xFF, DEC);
  Serial.print('.'); 
  Serial.println((versiondata>>8) & 0xFF, DEC);

  // Configure to read RFID tags
  nfc.SAMConfig();

  Serial.println("===================================");
  Serial.println("BomberCat Ready!");
  Serial.println("Waiting for NFC cards...");
  Serial.println("===================================");
}

void loop() {
  // Maintain MQTT connection
  if (!mqtt.connected()) {
    reconnectMQTT();
  }
  mqtt.loop();

  // Check for NFC card
  uint8_t success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success) {
    // Debounce
    if (millis() - lastNFCRead > 1000) {
      lastNFCRead = millis();

      Serial.println("\\nNFC Card Detected!");
      digitalWrite(LED_PIN, HIGH);

      // Convert UID to string
      String uidStr = "";
      Serial.print("UID: ");
      for (uint8_t i = 0; i < uidLength; i++) {
        if (uid[i] < 0x10) {
          uidStr += "0";
          Serial.print("0");
        }
        uidStr += String(uid[i], HEX);
        Serial.print(uid[i], HEX);
        if (i < uidLength - 1) Serial.print(":");
      }
      Serial.println();

      // Determine card type
      String cardType = "Unknown";
      if (uidLength == 4) {
        cardType = "Mifare Classic";
      } else if (uidLength == 7) {
        cardType = "Mifare Ultralight";
      }
      Serial.println("Type: " + cardType);

      // Send via MQTT
      String topic = String(MQTT_TOPIC_PREFIX) + "/nfc/read";
      String payload = "{\\"uid\\":\\"" + uidStr + "\\",";
      payload += "\\"type\\":\\"" + cardType + "\\",";
      payload += "\\"length\\":" + String(uidLength) + ",";
      payload += "\\"host\\":" + String(HOST_NUMBER) + "}";

      if (mqtt.publish(topic.c_str(), payload.c_str())) {
        Serial.println("MQTT: Published to " + topic);
      } else {
        Serial.println("MQTT: Failed to publish");
      }

      delay(200);
      digitalWrite(LED_PIN, LOW);
    }
  }

  delay(100);
}

void connectWiFi() {
  Serial.print("\\nConnecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\\nWiFi connection failed!");
  }

  digitalWrite(LED_PIN, LOW);
}

void reconnectMQTT() {
  while (!mqtt.connected()) {
    Serial.print("Connecting to MQTT broker at ");
    Serial.print(MQTT_SERVER);
    Serial.print(":");
    Serial.print(MQTT_PORT);
    Serial.print("...");

    if (mqtt.connect(MQTT_CLIENT_ID)) {
      Serial.println(" connected!");

      // Subscribe to command topic
      String cmdTopic = String(MQTT_TOPIC_PREFIX) + "/cmd";
      mqtt.subscribe(cmdTopic.c_str());
      Serial.println("Subscribed to: " + cmdTopic);

      // Publish online message
      String statusTopic = String(MQTT_TOPIC_PREFIX) + "/status";
      String statusMsg = "{\\"status\\":\\"online\\",\\"host\\":" + String(HOST_NUMBER) + "}";
      mqtt.publish(statusTopic.c_str(), statusMsg.c_str());

      // Flash LED to indicate connection
      for (int i = 0; i < 3; i++) {
        digitalWrite(LED_PIN, HIGH);
        delay(100);
        digitalWrite(LED_PIN, LOW);
        delay(100);
      }
    } else {
      Serial.print(" failed, rc=");
      Serial.print(mqtt.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("\\nMQTT message received [");
  Serial.print(topic);
  Serial.print("] ");

  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);

  // Handle commands
  if (message == "ping") {
    String pongTopic = String(MQTT_TOPIC_PREFIX) + "/pong";
    mqtt.publish(pongTopic.c_str(), "pong");

    // Blink LED
    digitalWrite(LED_PIN, HIGH);
    delay(50);
    digitalWrite(LED_PIN, LOW);
  } else if (message == "blink") {
    // Blink LED 5 times
    for (int i = 0; i < 5; i++) {
      digitalWrite(LED_PIN, HIGH);
      delay(200);
      digitalWrite(LED_PIN, LOW);
      delay(200);
    }
  } else if (message == "reboot") {
    Serial.println("Rebooting...");
    delay(1000);
    // RP2040 reset
    watchdog_enable(1, 1);
    while(1);
  }
}
"""

        sketch_file = sketch_dir / "BomberCat.ino"
        with open(sketch_file, 'w') as f:
            f.write(sketch_content)

        self.sketch_path = sketch_dir
        self.arduino.emit_log("Example firmware created successfully", "success")
        self.arduino.emit_progress(60)

        return str(self.sketch_path)

    def configure_firmware(self, wifi_ssid, wifi_pass, mqtt_server, mqtt_port, host_number):
        """Configure firmware parameters"""
        self.arduino.emit_log("Configuring firmware parameters...")
        self.arduino.emit_progress(65)

        if not self.sketch_path:
            raise Exception("No sketch path set")

        ino_files = list(self.sketch_path.glob("*.ino"))
        if not ino_files:
            raise Exception("No .ino file found")

        sketch_file = ino_files[0]

        with open(sketch_file, 'r') as f:
            content = f.read()

        config_header = f"""
// Auto-generated configuration by BomberCat Flasher
#ifndef BOMBERCAT_CONFIG_H
#define BOMBERCAT_CONFIG_H

// WiFi Configuration
#define WIFI_SSID "{wifi_ssid}"
#define WIFI_PASSWORD "{wifi_pass}"

// MQTT Configuration  
#define MQTT_SERVER "{mqtt_server}"
#define MQTT_PORT {mqtt_port}
#define MQTT_CLIENT_ID "BomberCat_{host_number}"
#define MQTT_TOPIC_PREFIX "bombercat/{host_number}"

// Host Configuration
#define HOST_NUMBER {host_number}

#endif // BOMBERCAT_CONFIG_H
"""

        config_file = self.sketch_path / "bombercat_config.h"
        with open(config_file, 'w') as f:
            f.write(config_header)

        if '#include "bombercat_config.h"' not in content:
            lines = content.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('//'):
                    insert_idx = i
                    break

            lines.insert(insert_idx, '#include "bombercat_config.h"')
            content = '\n'.join(lines)

            with open(sketch_file, 'w') as f:
                f.write(content)

        self.arduino.emit_log("Firmware configured successfully", "success")
        self.arduino.emit_progress(70)

    def compile_firmware(self, fqbn, port=None):
        """Compile firmware"""
        self.arduino.emit_log("Compiling firmware...")
        self.arduino.emit_progress(75)

        build_dir = Path(config.build_dir)
        build_dir.mkdir(exist_ok=True)

        cmd_args = [
            "compile",
            "--fqbn", fqbn,
            "--build-path", str(build_dir),
            str(self.sketch_path)
        ]

        if port:
            cmd_args.extend(["--port", port])

        try:
            self.arduino.run_command(*cmd_args)
            self.arduino.emit_log("Firmware compiled successfully", "success")
            self.arduino.emit_progress(85)
            return True
        except Exception as e:
            self.arduino.emit_log(f"Compilation error: {e}", "error")
            raise

    def flash_firmware(self, fqbn, port):
        """Flash firmware to device"""
        self.arduino.emit_log(f"Flashing firmware to {port}...")
        self.arduino.emit_progress(90)

        try:
            self.arduino.run_command(
                "upload",
                "--fqbn", fqbn,
                "--port", port,
                str(self.sketch_path)
            )

            self.arduino.emit_log("Firmware flashed successfully!", "success")
            self.arduino.emit_progress(100)
            return True

        except Exception as e:
            self.arduino.emit_log(f"Flash error: {e}", "error")
            raise

# Global instances
arduino_cli = ArduinoCLI(socketio)
firmware_manager = FirmwareManager(arduino_cli, socketio)

# Ensure directories exist
Path("tools").mkdir(exist_ok=True)
Path("build").mkdir(exist_ok=True)
Path("sketch").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

# Flask Routes
@app.route("/")
def index():
    """Serve the main web interface"""
    return render_template("index.html")

@app.route("/wizard")
def wizard():
    """Serve the Arduino flash wizard"""
    return render_template("wizard.html")

@app.route("/api/check_bootsel", methods=["GET"])
def check_bootsel():
    """Check if device is in BOOTSEL mode"""
    try:
        in_bootsel = False
        bootsel_path = None

        if platform.system() == "Windows":
            # Windows: Check all drive letters
            try:
                import win32api
                import win32file

                drives = []
                for letter in string.ascii_uppercase:
                    drive = f"{letter}:\\"
                    if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
                        drives.append(drive)

                for drive in drives:
                    try:
                        volume_info = win32api.GetVolumeInformation(drive)
                        if volume_info[0] == "RPI-RP2":
                            in_bootsel = True
                            bootsel_path = drive
                            break
                    except:
                        pass

            except ImportError:
                # Fallback without win32api
                for letter in string.ascii_uppercase:
                    test_path = Path(f"{letter}:/")
                    if test_path.exists():
                        info_file = test_path / "INFO_UF2.TXT"
                        if info_file.exists():
                            try:
                                with open(info_file, 'r') as f:
                                    content = f.read()
                                    if "RP2040" in content or "RPI-RP2" in content:
                                        in_bootsel = True
                                        bootsel_path = str(test_path)
                                        break
                            except:
                                pass

        elif platform.system() == "Darwin":  # macOS
            volumes_path = Path("/Volumes")
            if volumes_path.exists():
                for volume in volumes_path.iterdir():
                    if volume.name == "RPI-RP2":
                        in_bootsel = True
                        bootsel_path = str(volume)
                        break
                    info_file = volume / "INFO_UF2.TXT"
                    if info_file.exists():
                        try:
                            with open(info_file, 'r') as f:
                                if "RP2040" in f.read():
                                    in_bootsel = True
                                    bootsel_path = str(volume)
                                    break
                        except:
                            pass

        else:  # Linux
            mount_points = ["/media", "/mnt", "/run/media"]

            try:
                result = subprocess.run(['df', '-h'], capture_output=True, text=True)
                if 'RPI-RP2' in result.stdout:
                    in_bootsel = True
                    for line in result.stdout.split('\n'):
                        if 'RPI-RP2' in line:
                            parts = line.split()
                            if len(parts) >= 6:
                                bootsel_path = parts[5]
                            break
            except:
                pass

            import os
            for mount_base in mount_points:
                mount_path = Path(mount_base)
                if mount_path.exists():
                    for user_dir in mount_path.iterdir():
                        if user_dir.is_dir():
                            rpi_path = user_dir / "RPI-RP2"
                            if rpi_path.exists():
                                in_bootsel = True
                                bootsel_path = str(rpi_path)
                                break
                            info_file = user_dir / "INFO_UF2.TXT"
                            if info_file.exists():
                                try:
                                    with open(info_file, 'r') as f:
                                        if "RP2040" in f.read():
                                            in_bootsel = True
                                            bootsel_path = str(user_dir)
                                            break
                                except:
                                    pass
                    if in_bootsel:
                        break

            if not in_bootsel:
                try:
                    username = os.getenv('USER') or os.getenv('USERNAME')
                    if username:
                        user_media = Path(f"/media/{username}/RPI-RP2")
                        if user_media.exists():
                            in_bootsel = True
                            bootsel_path = str(user_media)
                except:
                    pass

        return jsonify({
            "in_bootsel": in_bootsel,
            "bootsel_path": bootsel_path,
            "platform": platform.system()
        })

    except Exception as e:
        arduino_cli.emit_log(f"Error checking BOOTSEL: {str(e)}", "warning")
        return jsonify({
            "in_bootsel": False, 
            "error": str(e),
            "platform": platform.system()
        })

@app.route("/api/check_dependencies", methods=["GET"])
def check_dependencies():
    """Check if Arduino CLI and dependencies are installed"""
    try:
        marker_file = Path(".dependencies_installed.json")
        if marker_file.exists():
            try:
                with open(marker_file, 'r') as f:
                    marker_data = json.load(f)
                    if marker_data.get("arduino_cli") and marker_data.get("boards"):
                        arduino_cli.initialized = True
                        return jsonify({
                            "arduino_cli": True,
                            "boards": True,
                            "initialized": True,
                            "from_marker": True
                        })
            except:
                pass

        arduino_installed = arduino_cli.cli_path and os.path.exists(arduino_cli.cli_path)

        boards_installed = False
        if arduino_installed:
            try:
                result = arduino_cli.run_command("core", "list")
                if result.stdout and 'rp2040:rp2040' in result.stdout:
                    boards_installed = True
            except:
                pass

        if installation_state["completed"]:
            arduino_installed = True
            boards_installed = True
            arduino_cli.initialized = True

        return jsonify({
            "arduino_cli": arduino_installed,
            "boards": boards_installed,
            "initialized": arduino_cli.initialized
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/install_dependencies", methods=["POST"])
def install_dependencies():
    """Install all dependencies"""
    if installation_state["in_progress"]:
        return jsonify({"status": "Installation already in progress"})

    def install_task():
        installation_state["in_progress"] = True
        installation_state["completed"] = False
        installation_state["error"] = False

        try:
            arduino_cli.initialize()
            arduino_cli.install_core("rp2040:rp2040")
            arduino_cli.install_libraries()

            arduino_cli.emit_log("All dependencies installed successfully!", "success")

            installation_state["completed"] = True
            installation_state["message"] = "All dependencies installed successfully!"

            socketio.emit('installation_complete', {
                'success': True,
                'message': installation_state["message"]
            }, room=None)

        except Exception as e:
            arduino_cli.emit_log(f"Installation failed: {str(e)}", "error")
            installation_state["error"] = True
            installation_state["message"] = str(e)

            socketio.emit('installation_complete', {
                'success': False,
                'message': installation_state["message"]
            }, room=None)

        finally:
            installation_state["in_progress"] = False

    thread = threading.Thread(target=install_task)
    thread.daemon = True
    thread.start()

    return jsonify({"status": "Installation started"})

@app.route("/api/detect_boards", methods=["GET"])
def detect_boards():
    """Detect connected BomberCat boards"""
    try:
        ports = []
        for port in serial.tools.list_ports.comports():
            port_info = {
                "port": port.device,
                "description": port.description,
                "hwid": port.hwid,
                "vid": port.vid,
                "pid": port.pid,
                "serial_number": port.serial_number,
                "manufacturer": port.manufacturer,
                "product": port.product,
                "likely_bombercat": False
            }

            # Check if it's likely a BomberCat (RP2040-based)
            if port.vid == 0x2E8A:  # Raspberry Pi vendor ID
                port_info['likely_bombercat'] = True
            elif port.vid == 0x239A:  # Adafruit vendor ID
                port_info['likely_bombercat'] = True
            elif "RP2040" in (port.description or ""):
                port_info['likely_bombercat'] = True
            elif "Pico" in (port.description or ""):
                port_info['likely_bombercat'] = True
            elif port.manufacturer and "Raspberry Pi" in port.manufacturer:
                port_info['likely_bombercat'] = True

            ports.append(port_info)

        # Check BOOTSEL mode
        bootsel_check = check_bootsel().get_json()

        return jsonify({
            "ports": ports,
            "in_bootsel": bootsel_check.get("in_bootsel", False),
            "bootsel_path": bootsel_check.get("bootsel_path")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/flash", methods=["POST"])
def flash():
    """Flash firmware with configuration"""
    data = request.get_json()

    port = data.get('port')
    wifi_ssid = data.get('wifi_ssid')
    wifi_pass = data.get('wifi_password')
    mqtt_server = data.get('mqtt_server', 'broker.hivemq.com')
    mqtt_port = data.get('mqtt_port', 1883)
    host_number = data.get('host_number', 1)
    fqbn = data.get('fqbn', config.arduino_fqbn)
    firmware_type = data.get('firmware_type', 'auto')

    if not all([port, wifi_ssid]):
        return jsonify({"error": "Missing required parameters"}), 400

    def flash_task():
        try:
            if firmware_type in ['host', 'client']:
                preference_file = Path(config.sketch_dir) / "relay_preference.txt"
                preference_file.write_text(firmware_type)
                arduino_cli.emit_log(f"Set firmware preference to: {firmware_type.upper()}", "info")

            firmware_manager.download_firmware()
            firmware_manager.configure_firmware(
                wifi_ssid, wifi_pass, mqtt_server, mqtt_port, host_number
            )
            firmware_manager.compile_firmware(fqbn, port)
            firmware_manager.flash_firmware(fqbn, port)

            arduino_cli.emit_log("BomberCat is ready to use!", "success")

        except Exception as e:
            arduino_cli.emit_log(f"Flash failed: {str(e)}", "error")

    thread = threading.Thread(target=flash_task)
    thread.daemon = True
    thread.start()

    return jsonify({"status": "Flash operation started"})

@app.route("/api/ports", methods=["GET"])
def get_ports():
    """Get available serial ports (legacy endpoint)"""
    return detect_boards()

@app.route("/api/status", methods=["GET"])
def get_status():
    """Get current status"""
    return jsonify({
        "initialized": arduino_cli.initialized,
        "arduino_cli_installed": bool(arduino_cli.cli_path),
        "flashing": False,
        "active": False,
        "mqtt_connected": False
    })

@app.route("/api/relay/start", methods=["POST"])
def start_relay():
    """Start relay (placeholder for compatibility)"""
    return jsonify({"status": "started"})

@app.route("/api/relay/stop", methods=["POST"])
def stop_relay():
    """Stop relay (placeholder for compatibility)"""
    return jsonify({"status": "stopped"})

@app.route("/api/firmware_info", methods=["GET"])
def firmware_info():
    """Get information about available firmwares"""
    sketch_dir = Path(config.sketch_dir)
    extracted_dir = sketch_dir / f"{config.repo_name}-main"
    firmware_dir = extracted_dir / "firmware"

    available_firmwares = []
    if firmware_dir.exists():
        for subdir in firmware_dir.iterdir():
            if subdir.is_dir():
                ino_files = list(subdir.glob("*.ino"))
                if ino_files:
                    fw_info = {
                        'name': subdir.name,
                        'type': 'unknown'
                    }

                    if 'host_relay_nfc' in subdir.name.lower():
                        fw_info['type'] = 'host'
                        fw_info['description'] = 'HOST device - connects to NFC reader'
                    elif 'client_relay_nfc' in subdir.name.lower():
                        fw_info['type'] = 'client'
                        fw_info['description'] = 'CLIENT device - emulates NFC card'
                    elif 'magspoof' in subdir.name.lower():
                        fw_info['type'] = 'magstripe'
                        fw_info['description'] = 'Magnetic stripe emulator'
                    elif 'detecttags' in subdir.name.lower():
                        fw_info['type'] = 'detector'
                        fw_info['description'] = 'NFC tag detector'

                    available_firmwares.append(fw_info)

    return jsonify({"firmwares": available_firmwares})

# SocketIO Events
@socketio.on('connect')
def handle_connect():
    emit('connected', {'data': 'Connected to BomberCat Arduino Flasher'})
    print(f"Client connected: {request.sid}")

    if installation_state["in_progress"]:
        emit('installation_status', {
            'in_progress': True,
            'message': 'Installation in progress...'
        })
    elif installation_state["completed"]:
        emit('installation_status', {
            'completed': True,
            'message': installation_state["message"]
        })

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('ping')
def handle_ping():
    emit('pong')

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": str(e)}), 500

# Main
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════╗
║      🔥 BOMBERCAT ARDUINO FLASHER 🔥         ║
╚══════════════════════════════════════════════╝

Complete firmware compilation and flash system
Direct from ElectronicCats/BomberCat repository

IMPORTANT: BomberCat uses RP2040, not ESP32!

This system will:
  ✓ Install Arduino CLI automatically
  ✓ Download firmware from GitHub
  ✓ Let you choose between HOST/CLIENT roles
  ✓ Configure WiFi and MQTT settings
  ✓ Compile and flash to your BomberCat
  ✓ Fix platform-specific compatibility issues
  ✓ Detect BOOTSEL mode automatically

Libraries included:
  ✓ All NFC libraries (PN532, PN7150)
  ✓ WiFi and communication libraries
  ✓ LED and hardware control libraries

Platform fixes:
  ✓ Uses correct FQBN for RP2040
  ✓ Installs RP2040 core
  ✓ Handles PN7150 library issues

For NFC Relay Attack, you need:
  • 2 BomberCat devices with NFC modules
  • Flash one as HOST (near reader)
  • Flash one as CLIENT (near card)

BOOTSEL Mode Instructions:
  • Hold BOOTSEL button while connecting USB
  • BomberCat will appear as RPI-RP2 drive
  • The wizard will detect this automatically

Starting server on http://localhost:{0}
""".format(config.flask_port))

    socketio.run(app, host=config.flask_host, port=config.flask_port, debug=config.flask_debug)
