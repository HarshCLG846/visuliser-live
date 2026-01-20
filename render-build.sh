#!/usr/bin/env bash
set -e

echo "Building Frontend..."
cd frontend
npm install
npm run build

echo "Moving Frontend build to Backend..."
rm -rf ../backend/static
mkdir -p ../backend/static
cp -r dist/* ../backend/static/

echo "Installing Backend Dependencies..."
cd ..
pip install -r requirements.txt
