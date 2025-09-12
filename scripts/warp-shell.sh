#!/bin/bash

# Script to open a warpified shell in the running API container
# Usage: ./scripts/warp-shell.sh

set -e

echo "🔍 Finding running API container..."

# Try to find the API container using docker compose first (preferred method)
CONTAINER_ID=$(docker compose ps -q api 2>/dev/null || true)

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ No API container found via docker compose. Trying to find by image/name..."
    
    # Fallback: search for container by name pattern or image
    CONTAINER_ID=$(docker ps --format "{{.ID}}" --filter "name=.*api.*" | head -n1)
    
    if [ -z "$CONTAINER_ID" ]; then
        # Another fallback: search by typical Django port
        CONTAINER_ID=$(docker ps --format "{{.ID}}" --filter "expose=8000" | head -n1)
    fi
fi

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ No running API container found!"
    echo "💡 Make sure your development environment is running with: make up"
    exit 1
fi

echo "✅ Found API container: $CONTAINER_ID"

# Setup warpify in the container
echo "🚀 Setting up Warp integration..."

# First, get the default user for this container
echo "📝 Detecting container user..."
DEFAULT_USER=$(docker exec "$CONTAINER_ID" whoami 2>/dev/null || echo "root")
echo "🔍 Container default user: $DEFAULT_USER"

# Setup warpify in the container user's home directory
echo "📝 Setting up Warp auto-warpify for $DEFAULT_USER..."
docker exec --user root "$CONTAINER_ID" bash -c '
    # Use the detected user
    ACTUAL_USER="'"$DEFAULT_USER"'"
    USER_HOME=$(eval echo ~$ACTUAL_USER)
    
    echo "🏠 User home directory: $USER_HOME"
    
    # Ensure user home directory and .bashrc exist
    mkdir -p "$USER_HOME"
    touch "$USER_HOME/.bashrc"
    
    # Set proper ownership if not root
    if [ "$ACTUAL_USER" != "root" ]; then
        chown -R $ACTUAL_USER:$ACTUAL_USER "$USER_HOME"
    fi
    
    # Check if warpify is already configured
    if grep -q "Auto-Warpify" "$USER_HOME/.bashrc" 2>/dev/null; then
        echo "✅ Warp auto-warpify already configured for $ACTUAL_USER!"
    else
        echo "📝 Adding Warp auto-warpify configuration to $USER_HOME/.bashrc..."
        echo -e "\n# Auto-Warpify" >> "$USER_HOME/.bashrc"
        echo "[[ \"\$-\" == *i* ]] && printf '\''\eP\$f{\"hook\": \"SourcedRcFileForWarp\", \"value\": { \"shell\": \"bash\", \"uname\": \"'\''$(uname)'\''\", \"tmux\": false }}\x9c'\'' " >> "$USER_HOME/.bashrc"
        
        # Ensure proper ownership of the .bashrc file if not root
        if [ "$ACTUAL_USER" != "root" ]; then
            chown $ACTUAL_USER:$ACTUAL_USER "$USER_HOME/.bashrc"
        fi
        echo "✅ Warp auto-warpify configured for $ACTUAL_USER!"
    fi
'

echo "🐚 Opening warpified shell in container $CONTAINER_ID..."
echo "📋 Container info:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" --filter "id=$CONTAINER_ID"
echo ""

# Check if running on macOS and Warp.app is available
if [[ "$OSTYPE" == "darwin"* ]] && [[ -d "/Applications/Warp.app" ]]; then
    echo "🍎 Opening Warp.app with container connection..."
    
    # The docker exec command to run
    DOCKER_CMD="docker exec -it $CONTAINER_ID /bin/bash"
    
    # Try multiple approaches for better compatibility
    
    # Method 1: Try opening Warp and copying command to clipboard
    echo "📋 Copying container connection command to clipboard..."
    echo "$DOCKER_CMD" | pbcopy
    
    # Open Warp.app
    open -a Warp.app
    
    # Wait a moment for Warp to open
    sleep 1
    
    # Try to create a new tab with the command
    osascript -e '
        tell application "Warp"
            activate
            delay 0.5
            tell application "System Events"
                keystroke "t" using command down
                delay 0.5
                keystroke "v" using command down
                delay 0.5
                key code 36
            end tell
        end tell
    ' 2>/dev/null || {
        echo "⚠️  Could not automatically paste command."
        echo "📋 Container connection command copied to clipboard: $DOCKER_CMD"
        echo "💡 Paste with Cmd+V and press Enter in the new Warp tab."
    }
    
    echo "✅ Warp.app opened!"
    echo "💡 If the command wasn't pasted automatically, use Cmd+V to paste: $DOCKER_CMD"
    
else
    echo "🐚 Opening shell in current terminal (fallback)..."
    # Fallback to current terminal
    docker exec -it "$CONTAINER_ID" /bin/bash
fi