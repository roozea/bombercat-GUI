# 🔥 Bombercat NFC Relay System with Real Flashing

Sistema avanzado de relay NFC con capacidad de flasheo real de firmware, interfaz web ultra moderna y comunicación en tiempo real.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v3.0.0-green.svg)
![SocketIO](https://img.shields.io/badge/socketio-v5.3.6-orange.svg)
![License](https://img.shields.io/badge/license-MIT-red.svg)

## 🚀 Nuevas Características de Flasheo

### Sistema de Flasheo Real
- **Detección automática de dispositivos**: Escanea todos los puertos USB disponibles
- **Soporte multi-protocolo**: ESP32, STM32, AVR y genérico
- **Gestión de firmware**: Local y remoto (repositorio GitHub)
- **Terminal en tiempo real**: Logs de flasheo con WebSocket
- **Barra de progreso**: Seguimiento visual del proceso
- **Verificación de integridad**: Checksum MD5
- **Reset automático**: Reinicia el dispositivo después del flasheo

### Proceso de Flasheo (Similar a BalenaEtcher)
1. **Selección de puerto**: Lista interactiva de dispositivos conectados
2. **Selección de firmware**: 
   - Archivos locales
   - Repositorio remoto
   - Drag & drop para subir
3. **Confirmación**: Resumen detallado antes de flashear
4. **Flasheo**: Terminal con logs en tiempo real
5. **Verificación**: Checksum y confirmación
6. **Reset**: Reinicio automático del dispositivo

## 📦 Instalación

### Requisitos previos
- Python 3.8 o superior
- Dispositivos Bombercat conectados vía USB
- Drivers USB instalados (CH340, CP2102, FTDI, etc.)

### Instalación rápida

```bash
# Clonar repositorio
git clone <repository-url>
cd bombercat-nfc-relay

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear directorios necesarios
mkdir templates firmwares

# Copiar archivos a sus ubicaciones
# bombercat_flasher.py -> raíz del proyecto
# index.html -> templates/
```

## 🔧 Configuración

### Variables de entorno (.env)

```env
# MQTT Configuration
MQTT_BROKER=broker.hivemq.com
MQTT_PORT=1883

# Serial Configuration
BOMBERCAT_PORT_1=/dev/ttyUSB0
BOMBERCAT_PORT_2=/dev/ttyUSB1

# Firmware Repository (opcional)
FIRMWARE_REPO_URL=https://api.github.com/repos/bombercat/firmwares/contents

# Firmware Directory
FIRMWARE_DIR=firmwares
```

## 🎮 Uso del Sistema de Flasheo

### 1. Iniciar el servidor

```bash
python bombercat_flasher.py
```

### 2. Abrir la interfaz web

Navegar a: `http://localhost:5000`

### 3. Proceso de flasheo

1. **Click en "START FLASH WIZARD"**
   - Se abrirá el asistente de flasheo

2. **Seleccionar puerto del dispositivo**
   - Lista todos los dispositivos USB conectados
   - Muestra información detallada (fabricante, serial, etc.)
   - Botón "REFRESH PORTS" para actualizar

3. **Seleccionar firmware**
   - **Tab Local**: Archivos en la carpeta `firmwares/`
   - **Tab Remote**: Descarga desde repositorio
   - **Upload**: Arrastra o selecciona archivo (.bin, .hex, .elf)

4. **Confirmar operación**
   - Revisa los detalles
   - Puerto seleccionado
   - Firmware elegido
   - Tamaño del archivo

5. **Flasheo en progreso**
   - Terminal con logs en tiempo real
   - Barra de progreso animada
   - Botón para cancelar si es necesario

6. **Completado**
   - Confirmación de éxito
   - Reset automático del dispositivo
   - Logs guardados

## 📡 Protocolos de Flasheo Soportados

### ESP32
```python
- Baudrate: 921600
- Reset sequence: DTR/RTS toggle
- Sync command: 0xC0 based protocol
- Chunk size: 1024 bytes
```

### STM32
```python
- Baudrate: 115200
- Boot mode: BOOT0 pin high
- Protocol: STM32 UART bootloader
- Chunk size: 256 bytes
```

### AVR (Arduino)
```python
- Baudrate: 115200
- Protocol: STK500
- Chunk size: 128 bytes
```

## 🔍 Estructura del Proyecto

```
bombercat-nfc-relay/
├── bombercat_flasher.py   # Backend con soporte de flasheo
├── templates/
│   └── index.html         # Interfaz web mejorada
├── firmwares/             # Directorio de firmwares locales
│   ├── bombercat_v1.0.bin
│   └── bombercat_v1.1.bin
├── requirements.txt       # Dependencias
├── .env                   # Configuración
└── README.md             # Este archivo
```

## 🛠️ API Endpoints

### Flasheo
- `GET /api/ports` - Lista puertos seriales disponibles
- `GET /api/firmwares/local` - Lista firmwares locales
- `GET /api/firmwares/remote` - Lista firmwares del repositorio
- `POST /api/firmware/upload` - Subir archivo de firmware
- `POST /api/firmware/download` - Descargar del repositorio
- `POST /api/flash` - Iniciar proceso de flasheo

### WebSocket Events
- `connect` - Conexión establecida
- `flash_log` - Mensaje de log del flasheo
- `flash_progress` - Actualización de progreso

## 🎨 Características de la Interfaz

- **Diseño Cyberpunk**: Manteniendo el estilo sexy original
- **Animaciones fluidas**: Transiciones y efectos visuales
- **Terminal integrado**: Logs de flasheo en tiempo real
- **Modales interactivos**: Para cada paso del proceso
- **Drag & Drop**: Para subir firmwares fácilmente
- **Responsive**: Funciona en móviles y tablets

## 🔒 Seguridad

- Validación de archivos de firmware
- Checksum MD5 para integridad
- Límite de tamaño de archivo (16MB)
- Extensiones permitidas: .bin, .hex, .elf
- Timeout configurable para operaciones

## 🐛 Solución de Problemas

### "No devices found"
```bash
# Linux: Agregar usuario al grupo dialout
sudo usermod -a -G dialout $USER
# Logout y login para aplicar

# Verificar permisos
ls -la /dev/ttyUSB*
```

### "Flash failed: timeout"
- Verificar que el dispositivo esté en modo bootloader
- Intentar con baudrate más bajo
- Revisar conexión USB

### "Permission denied"
```bash
# Linux/Mac
sudo chmod 666 /dev/ttyUSB0

# O ejecutar con sudo (no recomendado)
sudo python bombercat_flasher.py
```

## 📝 Logs de Ejemplo

```
[12:34:56] Detecting chip type...
[12:34:57] Detected ESP32
[12:34:57] Resetting device into bootloader mode...
[12:34:58] Device reset complete
[12:34:58] Reading firmware file: firmwares/bombercat_v1.1.bin
[12:34:58] Firmware size: 245760 bytes
[12:34:58] Checksum: a1b2c3d4e5f6789
[12:34:59] Starting flash process...
[12:35:00] Erasing flash memory...
[12:35:05] Writing 240 chunks of 1024 bytes
[12:35:15] Written 100/240 chunks
[12:35:25] Firmware write complete
[12:35:26] Verifying firmware...
[12:35:28] Firmware verified successfully
[12:35:28] Resetting device to run new firmware...
[12:35:29] Flash complete! Device is running new firmware
```

## 🚀 Características Avanzadas

### Auto-detección de chip
El sistema detecta automáticamente el tipo de microcontrolador:
- ESP32/ESP8266
- STM32F103/F401/etc
- ATmega328P/32U4/etc

### Modo de recuperación
Si el flasheo falla, el sistema intenta:
1. Reset forzado del dispositivo
2. Cambio de baudrate
3. Protocolo alternativo

### Verificación post-flasheo
- Lee el firmware del dispositivo
- Compara checksums
- Confirma la operación

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:
1. Fork el proyecto
2. Crea tu feature branch
3. Commit tus cambios
4. Push al branch
5. Abre un Pull Request

## ⚠️ Disclaimer

Este software es para fines educativos. El flasheo incorrecto puede dañar permanentemente tu dispositivo. Úsalo bajo tu propio riesgo.

## 📄 Licencia

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8+
- pip
- Dispositivos Bombercat compatibles

### Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/bombercat-GUI.git
cd bombercat-GUI
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus configuraciones específicas
```

### Uso

1. **Ejecutar la aplicación:**
```bash
python main.py
```

2. **Acceder a la interfaz web:**
   - Abrir navegador en `http://localhost:5000`

## 📁 Estructura del Proyecto

```
bombercat-GUI/
├── main.py                 # Aplicación principal Flask
├── bombercat_relay.py      # Lógica de relay NFC
├── firmware_helper.py      # Utilidades para firmware
├── select_firmware.py      # Selector de firmware
├── switch_firmware.py      # Cambiador de firmware
├── templates/              # Plantillas HTML
│   ├── index.html         # Interfaz principal
│   └── wizard.html        # Asistente de configuración
├── static/                # Archivos estáticos (CSS, JS, imágenes)
├── sketch/                # Código Arduino/ESP32
├── requirements.txt       # Dependencias Python
├── .env.example          # Plantilla de configuración
└── setup.sh              # Script de configuración
```

## ⚙️ Configuración

Edita el archivo `.env` con tus configuraciones:

```env
# Configuración MQTT
MQTT_BROKER=tu-broker.com
MQTT_PORT=1883
MQTT_USERNAME=tu_usuario
MQTT_PASSWORD=tu_contraseña

# Puertos Serie
BOMBERCAT_PORT_1=/dev/ttyUSB0
BOMBERCAT_PORT_2=/dev/ttyUSB1

# Ruta del Firmware
FIRMWARE_PATH=ruta/a/tu/firmware.bin
```

## 🔧 Scripts Disponibles

- `run.sh` - Ejecutar la aplicación
- `restart_server.sh` - Reiniciar servidor
- `setup.sh` - Configuración inicial

## 🛡️ Seguridad

- **NUNCA** subas archivos `.env` al repositorio
- Mantén tus credenciales MQTT seguras
- Usa contraseñas fuertes para servicios externos

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles

---

**¿Necesitas ayuda?** Abre un issue en GitHub o contacta al equipo de desarrollo.