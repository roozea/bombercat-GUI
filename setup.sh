#!/bin/bash
# Bombercat NFC Relay Setup Script

echo "🔥 Bombercat NFC Relay System Setup"
echo "===================================="

# Check Python version
python_version=$(python3 --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi
echo "✅ Found $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
if [[ $? -ne 0 ]]; then
    echo "❌ Error creating virtual environment"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [[ $? -ne 0 ]]; then
    echo "❌ Error installing dependencies"
    exit 1
fi

# Create templates directory
echo "📁 Creating templates directory..."
mkdir -p templates

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

# Create dummy firmware file if it doesn't exist
if [ ! -f bombercat_firmware.bin ]; then
    echo "📄 Creating dummy firmware file..."
    echo "DUMMY_FIRMWARE_DATA" > bombercat_firmware.bin
fi

# Check serial ports
echo ""
echo "🔌 Available serial ports:"
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    ls /dev/tty* 2>/dev/null | grep -E "(USB|ACM)" || echo "No USB serial ports found"
else
    echo "Please check Device Manager for COM ports (Windows)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Edit the .env file with your serial port configuration"
echo "3. Run: python bombercat_relay.py"
echo ""
echo "Web interface will be available at: http://localhost:8081"