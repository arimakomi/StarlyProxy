#!/bin/bash
#
# StarlyProxy CLI Wrapper
# Ensures venv is activated before running CLI
#

INSTALL_DIR="/opt/starlyproxy"
VENV_DIR="$INSTALL_DIR/venv"
CLI_SCRIPT="$INSTALL_DIR/cli/starlyproxy-cli.py"

# Check if running from installed location
if [ ! -d "$INSTALL_DIR" ]; then
    # Development mode - try current directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    VENV_DIR="$SCRIPT_DIR/venv"
    CLI_SCRIPT="$SCRIPT_DIR/cli/starlyproxy-cli.py"
fi

# Activate venv if exists
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
fi

# Run CLI with all arguments
if [ -f "$CLI_SCRIPT" ]; then
    python3 "$CLI_SCRIPT" "$@"
else
    echo "Error: CLI script not found at $CLI_SCRIPT"
    echo "Please ensure StarlyProxy is installed correctly."
    exit 1
fi
