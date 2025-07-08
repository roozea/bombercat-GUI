#!/bin/bash
# Restart BomberCat Arduino Flasher with fixes

echo "🔥 Restarting BomberCat Arduino Flasher with fixes..."
echo ""

# Kill any existing Python processes running on port 8081
echo "Stopping existing server..."
lsof -ti:8081 | xargs kill -9 2>/dev/null

# Wait a moment
sleep 2

# Clear any existing Arduino CLI state
echo "Clearing Arduino CLI state..."
rm -rf ~/.arduino15/arduino-cli.yaml 2>/dev/null

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Start the server
echo "Starting server with fixes..."
echo ""
python bombercat_relay.py