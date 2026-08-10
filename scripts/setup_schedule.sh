#!/bin/bash
set -e

echo "Setting up SCOUT launch agents..."

# Define paths
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PROJECT_DIR="/Users/varunsaiandra/Desktop/SCOUT"

# Ensure the LaunchAgents directory exists
mkdir -p "$LAUNCH_AGENTS_DIR"

# Copy the plists
cp "$PROJECT_DIR/launchagents/com.scout.processor.plist" "$LAUNCH_AGENTS_DIR/"
cp "$PROJECT_DIR/launchagents/com.scout.delivery.plist" "$LAUNCH_AGENTS_DIR/"

# Unload existing if they exist (ignore errors if they don't)
launchctl unload "$LAUNCH_AGENTS_DIR/com.scout.processor.plist" 2>/dev/null || true
launchctl unload "$LAUNCH_AGENTS_DIR/com.scout.delivery.plist" 2>/dev/null || true

# Load the new plists
launchctl load "$LAUNCH_AGENTS_DIR/com.scout.processor.plist"
launchctl load "$LAUNCH_AGENTS_DIR/com.scout.delivery.plist"

echo "Launch agents installed and loaded."
echo ""
echo "Current loaded SCOUT jobs:"
launchctl list | grep scout || true
echo ""
echo "Setting up pmset wake schedule..."
echo "(This will require your sudo password)"
sudo pmset repeat wake MTWRFSU 01:59:00

echo "SCOUT scheduling setup complete!"
