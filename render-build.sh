#!/usr/bin/env bash
set -e

echo "Building Frontend..."
cd frontend
npm install
npm run build

echo "Installing Backend Dependencies..."
cd ..
pip install -r requirements.txt
