#!/usr/bin/env bash
# Build script for Render deployment

echo "🚀 Starting TrueSign build process..."

# Update pip
pip install --upgrade pip setuptools wheel

# Install system dependencies for ML libraries
apt-get update
apt-get install -y build-essential libomp-dev

# Install Python dependencies
pip install --no-cache-dir -r requirements.txt

echo "✅ Build completed successfully!"
