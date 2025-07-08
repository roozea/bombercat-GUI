# 🔥 BomberCat Arduino Flash Wizard

Sistema completo de compilación y flasheo de firmware para BomberCat con integración de Arduino CLI, descarga automática desde GitHub y configuración interactiva.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Arduino](https://img.shields.io/badge/arduino-cli-00979D.svg)
![ESP32](https://img.shields.io/badge/esp32-supported-orange.svg)

## 🚀 Características Principales

### Sistema Completo de Flasheo
- **Detección automática** de dispositivos BomberCat vía USB
- **Instalación automática** de Arduino CLI (no necesitas instalarlo manualmente)
- **Descarga directa** del firmware desde [ElectronicCats/BomberCat](https://github.com/ElectronicCats/BomberCat)
- **Configuración interactiva** de WiFi, MQTT y parámetros del dispositivo
- **Compilación en tiempo real** con logs detallados
- **Flasheo con progreso** y verificación

### Wizard Paso a Paso
1. **Detectar Dispositivo** - Identifica automáticamente placas ESP32
2. **Instalar Dependencias** - Arduino CLI, ESP32 core, librerías
3. **Configurar** - WiFi, MQTT, número de host
4. **Flashear** - Compila y carga el firmware

## 📦 Instalación Rápida

### Requisitos
- Python 3.8 o superior
- Conexión a internet (para descargar dependencias)
- Dispositivo BomberCat conectado vía USB

### Pasos de Instalación

```bash
# 1. Clonar o descargar los archivos
mkdir bombercat-flasher
cd bombercat-flasher

# 2. Copiar los archivos:
# - bombercat_arduino_flasher.py
# - templates/index.html
# - requirements.txt
# - setup_arduino.sh

# 3. Dar permisos de ejecución
chmod +x setup_arduino.sh

# 4. Ejecutar el instalador
./setup_arduino.sh

# 5. Iniciar el flasher
./run_arduino_flasher.sh
```

## 🎮 Uso del Sistema

### 1. Iniciar el Wizard

```bash
./run_arduino_flasher.sh
```

Abre tu navegador en: `http://localhost:5000`

### 2. Paso 1: Detectar Dispositivo

- Conecta tu BomberCat vía USB
- Click en "REFRESH DEVICES"
- Selecciona tu dispositivo (busca los marcados con 🔥)
- Los dispositivos ESP32 se detectan automáticamente

### 3. Paso 2: Instalar Dependencias

El sistema instalará automáticamente:
- **Arduino CLI** - Herramienta de línea de comandos
- **ESP32 Board Support** - Definiciones y herramientas de Espressif
- **Librerías Requeridas**:
  - WiFiManager - Gestión de WiFi
  - PubSubClient - Cliente MQTT
  - ArduinoJson - Parsing JSON
  - Adafruit PN532 - Soporte NFC

### 4. Paso 3: Configuración

Configura los parámetros de tu BomberCat:

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| WiFi SSID | Nombre de tu red WiFi | `MiRedWiFi` |
| WiFi Password | Contraseña WiFi | `••••••••` |
| MQTT Broker | Servidor MQTT | `broker.hivemq.com` |
| MQTT Port | Puerto MQTT | `1883` |
| Host Number | ID único del dispositivo | `1` |

### 5. Paso 4: Flasheo

El sistema automáticamente:
1. Descarga el firmware más reciente de GitHub
2. Configura los parámetros en el código
3. Compila el firmware
4. Flashea al dispositivo
5. Verifica la operación

## 🔧 Estructura del Proyecto

```
bombercat-flasher/
├── bombercat_arduino_flasher.py  # Backend principal
├── templates/
│   └── index.html               # Interfaz web del wizard
├── tools/                       # Arduino CLI (auto-instalado)
├── build/                       # Archivos de compilación
├── sketch/                      # Firmware descargado
├── requirements.txt             # Dependencias Python
├── run_arduino_flasher.sh       # Script de ejecución
└── README_ARDUINO.md           # Este archivo
```

## 📡 Configuración Avanzada

### Variables de Entorno (.env)

```env
# Puerto del servidor web
FLASK_PORT=5000

# Versión de Arduino CLI
ARDUINO_CLI_VERSION=0.35.3

# FQBN por defecto
ARDUINO_FQBN=esp32:esp32:esp32

# Repositorio de firmware
REPO_OWNER=ElectronicCats
REPO_NAME=BomberCat
```

### Configuración de Placa Personalizada

Para usar una placa ESP32 específica, modifica el FQBN:

- ESP32 genérico: `esp32:esp32:esp32`
- ESP32 DevKit V1: `esp32:esp32:esp32doit-devkit-v1`
- ESP32 Wrover: `esp32:esp32:esp32wrover`

## 🐛 Solución de Problemas

### "No devices found"

**Linux/Mac:**
```bash
# Agregar usuario al grupo dialout
sudo usermod -a -G dialout $USER
# Cerrar sesión y volver a iniciar

# Verificar permisos
ls -la /dev/ttyUSB*
```

**Windows:**
- Instalar drivers CH340/CP2102
- Verificar en Administrador de Dispositivos

### "Arduino CLI download failed"

- Verificar conexión a internet
- Verificar permisos de escritura en carpeta `tools/`
- Descargar manualmente desde [Arduino CLI Releases](https://github.com/arduino/arduino-cli/releases)

### "Compilation error"

- Verificar que el dispositivo sea compatible con ESP32
- Revisar logs detallados en la terminal web
- Asegurarse de que las librerías estén instaladas

### "Upload failed"

- Verificar que el puerto no esté en uso
- Intentar presionar el botón BOOT durante el upload
- Reducir la velocidad de upload en la configuración

## 📊 Logs de Ejemplo

```
[12:34:56] Downloading Arduino CLI...
[12:34:58] Arduino CLI installed successfully
[12:35:00] Installing esp32:esp32 core...
[12:35:45] esp32:esp32 core installed
[12:35:46] Installing required libraries...
[12:36:10] Libraries installed
[12:36:15] Downloading BomberCat firmware from GitHub...
[12:36:18] Firmware downloaded successfully
[12:36:19] Configuring firmware parameters...
[12:36:20] Firmware configured successfully
[12:36:21] Compiling firmware...
[12:37:05] Firmware compiled successfully
[12:37:06] Flashing firmware to /dev/ttyUSB0...
[12:37:35] Firmware flashed successfully!
[12:37:36] BomberCat is ready to use!
```

## 🔍 Arquitectura del Sistema

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Browser   │────▶│  Flask Server   │────▶│  Arduino CLI    │
│   (Wizard UI)   │     │  (WebSocket)    │     │  (Compiler)     │
└─────────────────┘     └────────┬────────┘     └────────┬────────┘
                                 │                        │
                                 ▼                        ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │     GitHub      │     │   BomberCat     │
                        │   Repository    │     │   Device        │
                        └─────────────────┘     └─────────────────┘
```

## 🚀 Características Avanzadas

### Multi-dispositivo
Puedes flashear múltiples BomberCats con diferentes configuraciones:
- Cada uno con su propio Host Number
- Configuraciones WiFi/MQTT independientes
- Flasheo secuencial o paralelo

### Firmware Personalizado
El sistema modifica automáticamente el firmware para incluir:
- Credenciales WiFi hardcodeadas
- Configuración MQTT
- ID único del dispositivo

### Compilación Optimizada
- Cache de compilación para flasheos más rápidos
- Reutilización de librerías descargadas
- Compilación incremental

## 🔒 Seguridad

- Las credenciales WiFi se compilan en el firmware (no se transmiten)
- Opción de usar MQTT con TLS
- Los logs no muestran contraseñas

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch
3. Commit tus cambios
4. Push al branch
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. El firmware de BomberCat tiene su propia licencia en el [repositorio oficial](https://github.com/ElectronicCats/BomberCat).

## 🙏 Agradecimientos

- [Electronic Cats](https://github.com/ElectronicCats) por el firmware BomberCat
- [Arduino](https://www.arduino.cc/) por Arduino CLI
- Comunidad ESP32 por el soporte de placas

---

**¿Necesitas ayuda?** Abre un issue o contacta al equipo de desarrollo.

**Happy Hacking! 🔥**