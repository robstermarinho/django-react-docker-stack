#!/bin/bash

# Script to open a warpified shell in the running container
# Usage: ./scripts/warp-shell.sh [container_name]
# Example: ./scripts/warp-shell.sh api

set -e

# Get container name from parameter or default to 'api'
CONTAINER_NAME="${1:-api}"

echo "🔍 Finding running $CONTAINER_NAME container..."

# Try to find the container using docker compose first (preferred method)
CONTAINER_ID=$(docker compose ps -q "$CONTAINER_NAME" 2>/dev/null || true)

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ No $CONTAINER_NAME container found via docker compose. Trying to find by image/name..."
    
    # Fallback: search for container by name pattern
    CONTAINER_ID=$(docker ps --format "{{.ID}}" --filter "name=.*$CONTAINER_NAME.*" | head -n1)
    
    if [ -z "$CONTAINER_ID" ] && [ "$CONTAINER_NAME" = "api" ]; then
        # Another fallback for API: search by typical Django port
        CONTAINER_ID=$(docker ps --format "{{.ID}}" --filter "expose=8000" | head -n1)
    fi
fi

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ No running $CONTAINER_NAME container found!"
    echo "💡 Make sure your development environment is running with: make up"
    exit 1
fi

echo "✅ Found $CONTAINER_NAME container: $CONTAINER_ID"

# Setup warpify in the container
echo "🚀 Setting up Warp integration..."

# First, get the default user and available shell for this container
echo "📝 Detecting container user and shell..."
DEFAULT_USER=$(docker exec "$CONTAINER_ID" whoami 2>/dev/null || echo "root")

# Detect available shell (bash preferred, fallback to sh)
if docker exec "$CONTAINER_ID" which bash >/dev/null 2>&1; then
    SHELL_CMD="bash"
elif docker exec "$CONTAINER_ID" which sh >/dev/null 2>&1; then
    SHELL_CMD="sh"
else
    echo "❌ No compatible shell found in container!"
    exit 1
fi

echo "🔍 Container default user: $DEFAULT_USER"
echo "🐚 Available shell: $SHELL_CMD"

# Setup warpify in the container user's home directory
echo "📝 Setting up Warp auto-warpify for $DEFAULT_USER..."
docker exec --user root "$CONTAINER_ID" $SHELL_CMD -c '
    # Use the detected user and shell
    ACTUAL_USER="'"$DEFAULT_USER"'"
    SHELL_CMD="'"$SHELL_CMD"'"
    USER_HOME=$(eval echo ~$ACTUAL_USER)
    
    echo "🏠 User home directory: $USER_HOME"
    echo "🐚 Using shell: $SHELL_CMD"
    
    # Determine config file based on shell
    if [ "$SHELL_CMD" = "bash" ]; then
        CONFIG_FILE="$USER_HOME/.bashrc"
        SHELL_TYPE="bash"
    else
        CONFIG_FILE="$USER_HOME/.profile"
        SHELL_TYPE="sh"
    fi
    
    echo "📄 Config file: $CONFIG_FILE"
    
    # Ensure user home directory and config file exist
    mkdir -p "$USER_HOME"
    touch "$CONFIG_FILE"
    
    # Set proper ownership if not root
    if [ "$ACTUAL_USER" != "root" ]; then
        chown -R $ACTUAL_USER:$ACTUAL_USER "$USER_HOME"
    fi
    
    # Check if warpify is already configured
    if grep -q "Auto-Warpify" "$CONFIG_FILE" 2>/dev/null; then
        echo "✅ Warp auto-warpify already configured for $ACTUAL_USER!"
    else
        echo "📝 Adding Warp auto-warpify configuration to $CONFIG_FILE..."
        echo -e "\n# Auto-Warpify" >> "$CONFIG_FILE"
        
        # Use appropriate shell detection syntax
        if [ "$SHELL_CMD" = "bash" ]; then
            echo "[[ \"\$-\" == *i* ]] && printf '\''\eP\$f{\"hook\": \"SourcedRcFileForWarp\", \"value\": { \"shell\": \"bash\", \"uname\": \"'\''$(uname)'\''\", \"tmux\": false }}\x9c'\'' " >> "$CONFIG_FILE"
        else
            echo "case \$- in *i*) printf '\''\eP\$f{\"hook\": \"SourcedRcFileForWarp\", \"value\": { \"shell\": \"sh\", \"uname\": \"'\''$(uname)'\''\", \"tmux\": false }}\x9c'\'' ;; esac" >> "$CONFIG_FILE"
        fi
        
        # Ensure proper ownership of the config file if not root
        if [ "$ACTUAL_USER" != "root" ]; then
            chown $ACTUAL_USER:$ACTUAL_USER "$CONFIG_FILE"
        fi
        echo "✅ Warp auto-warpify configured for $ACTUAL_USER using $SHELL_TYPE!"
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
    DOCKER_CMD="docker exec -it $CONTAINER_ID $SHELL_CMD"
    
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
    docker exec -it "$CONTAINER_ID" $SHELL_CMD
fi