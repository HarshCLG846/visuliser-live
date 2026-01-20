#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Build started..."

# 1. Build Frontend
echo "Building Frontend..."
cd frontend
npm install
npm audit fix --force   # optional
npm run build
cd ..

# 2. Move build artifacts to backend
echo "Moving Frontend build to Backend..."
# Create static directory if it doesn't exist
mkdir -p backend/static

# Remove old files to ensure clean state
rm -rf backend/static/*

# Copy build output (assuming dist is the output folder from Vite)
cp -r frontend/dist/* backend/static/

# 3. Install Backend Dependencies
echo "Installing Backend Dependencies..."
pip install -r requirements.txt

echo "Build finished successfully!"
