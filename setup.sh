#!/usr/bin/env bash
set -e

echo "=========================================="
echo "Setting up Inference Dashboard"
echo "=========================================="

# Check Python version
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing requirements..."
pip install -r requirements.txt

# Create systemd service
echo "Creating systemd service..."
sudo nano ~/inference-dashboard.service

# Enable and start service
echo "Enabling service..."
sudo systemctl enable inference-dashboard.service

echo "Starting service..."
sudo systemctl start inference-dashboard.service

# Check status
echo "Service status:"
sudo systemctl status inference-dashboard.service

echo ""
echo "=========================================="
echo "Dashboard is ready!"
echo "Access at: http://localhost:5000"
echo "=========================================="
