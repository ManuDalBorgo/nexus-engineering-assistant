#!/bin/bash
echo "Starting Nexus Engineering Assistant Demo..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment using /usr/bin/python3..."
    /usr/bin/python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip to ensure we can install modern packages
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r backend/requirements.txt

# Run Streamlit app
# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed. The 'Local' model option will not work."
    echo "   To use local models, install from https://ollama.com"
else
    # Check if server is running (basic check)
    if ! pgrep -x "ollama" > /dev/null; then
        echo "⚠️  Ollama is installed but not running."
        echo "   Starting Ollama in the background..."
        ollama serve &
        sleep 5
    fi
    
    # Check if llama3 is pulled
    if ! ollama list | grep -q "llama3"; then
        echo "⬇️  Pulling Llama 3 model (this may take a while)..."
        ollama pull llama3
    fi
fi

echo "Starting Frontend..."
streamlit run frontend/app.py
