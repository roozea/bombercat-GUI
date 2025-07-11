# RP2040 Compatibility Guide for BomberCat Firmware

## Overview

This guide documents the changes made to make the BomberCat host_Relay_NFC firmware compatible with the Raspberry Pi Pico (RP2040) using Earle Philhower's Arduino core.

## Problem Statement

The original firmware used mbed-specific features that are not available in the RP2040 Arduino core:
- `using namespace mbed;`
- `FlashIAPBlockDevice`
- `TDBStore`
- `getFlashIAPLimits()`
- `MBED_SUCCESS` and `MBED_ERROR_ITEM_NOT_FOUND` constants

## Solution Overview

The firmware has been modified to be platform-compatible, supporting both MBED and RP2040 platforms through conditional compilation.

## Changes Made

### 1. Platform Detection (`FlashIAPLimits.h`)

Added platform-specific defines:
```cpp
#ifdef ARDUINO_ARCH_RP2040
  #define BOMBERCAT_RP2040
#endif

#ifdef ARDUINO_ARCH_MBED
  #define BOMBERCAT_MBED
#endif
```

### 2. Conditional Includes (`host_Relay_NFC.ino`)

```cpp
#ifdef BOMBERCAT_MBED
#include <FlashIAPBlockDevice.h>
#include <TDBStore.h>
using namespace mbed;
#endif

#ifdef BOMBERCAT_RP2040
#include <EEPROM.h>
#endif
```

### 3. Storage System Abstraction

#### Platform-Compatible Constants
```cpp
#ifdef BOMBERCAT_MBED
#define STORAGE_SUCCESS MBED_SUCCESS
#define STORAGE_ERROR_ITEM_NOT_FOUND MBED_ERROR_ITEM_NOT_FOUND
#else
#define STORAGE_SUCCESS 0
#define STORAGE_ERROR_ITEM_NOT_FOUND -1
#endif
```

#### Storage Initialization
```cpp
#ifdef BOMBERCAT_MBED
  auto result = store.init();
#else
  EEPROM.begin(EEPROM_SIZE);
  auto result = STORAGE_SUCCESS;
#endif
```

### 4. Storage Functions

#### getSketchStats Function
- **MBED**: Uses `TDBStore` with `store.get_info()` and `store.get()`
- **RP2040**: Uses EEPROM with magic number validation

#### setSketchStats Function
- **MBED**: Uses `store.set()`
- **RP2040**: Uses `EEPROM.put()` with magic number and `EEPROM.commit()`

### 5. Flash Limits Function (`FlashIAPLimits.h`)

```cpp
FlashIAPLimits getFlashIAPLimits()
{
#ifdef BOMBERCAT_MBED
  // Original mbed implementation
#else
  // RP2040 platform - return dummy values since we'll use EEPROM instead
  return { 2048 * 1024, 0, 4096 }; // 2MB flash, 4KB available for storage
#endif
}
```

## How to Use

### Prerequisites

1. **Install Earle Philhower's RP2040 Arduino Core:**
   ```bash
   # Add to Arduino IDE Board Manager URLs:
   https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json
   ```

2. **Install Required Libraries:**
   - WiFiNINA
   - PubSubClient
   - SerialCommand
   - EEPROM (included with RP2040 core)

### Compilation

1. **Select Board:** `Raspberry Pi Pico` or `Raspberry Pi Pico W`
2. **FQBN:** `rp2040:rp2040:rpipico`
3. **Compile:** The firmware will automatically detect the RP2040 platform and use EEPROM storage

### Arduino CLI Command
```bash
arduino-cli compile --fqbn rp2040:rp2040:rpipico sketch/BomberCat-main/firmware/host_Relay_NFC/host_Relay_NFC.ino
```

## Storage Behavior

### MBED Platform
- Uses FlashIAP block device with TDBStore
- Persistent storage in internal flash
- Key-value store with metadata

### RP2040 Platform
- Uses EEPROM emulation (stored in flash)
- 4KB storage space allocated
- Magic number (`0xDEADBEEF`) for data validation
- Simple binary storage of SketchStats structure

## Configuration Data Stored

The firmware stores the following configuration:
- WiFi SSID and password
- MQTT server address
- Host number
- Track data

## Testing

To test the compilation:
```bash
python3 test_rp2040_compilation.py
```

## Troubleshooting

### Common Issues

1. **Library Not Found Errors:**
   - Ensure all required libraries are installed
   - Check library compatibility with RP2040

2. **EEPROM Issues:**
   - The RP2040 EEPROM is emulated in flash
   - Call `EEPROM.begin(size)` before use
   - Call `EEPROM.commit()` to save changes

3. **Memory Issues:**
   - RP2040 has 264KB RAM vs mbed platforms
   - Monitor memory usage if issues occur

### Alternative Cores

If you prefer to use a different core that supports mbed:
1. **Arduino Mbed OS RP2040 Boards** - Official Arduino core with mbed support
2. **PlatformIO with mbed framework** - Full mbed compatibility

## Files Modified

1. `sketch/BomberCat-main/firmware/host_Relay_NFC/host_Relay_NFC.ino`
2. `sketch/BomberCat-main/firmware/host_Relay_NFC/FlashIAPLimits.h`

## Backward Compatibility

The changes maintain full backward compatibility with mbed platforms. The original functionality is preserved when compiling for mbed-compatible boards.

## Future Improvements

1. **LittleFS Support:** Could replace EEPROM with LittleFS for better file system support
2. **Preferences Library:** Alternative storage option for ESP32-like behavior
3. **Dynamic Memory Management:** Optimize memory usage for RP2040's constraints

## Conclusion

The firmware is now compatible with both mbed and RP2040 platforms, allowing users to choose their preferred development environment while maintaining the same functionality.