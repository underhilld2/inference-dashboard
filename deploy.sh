#!/usr/bin/env bash
set -e

echo "=========================================="
echo "Inference Dashboard Installation Script"
echo "=========================================="

# Check prerequisites
python3 --version
python3 -m venv venv
source venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --break-system-packages

echo ""
echo "Creating directories..."
mkdir -p data reports

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "To start services:"
echo "  sudo systemctl start inference-dashboard.service"
echo "  sudo systemctl start data-collector.service"
echo ""
echo "Dashboard: http://localhost:5000"
echo ""
