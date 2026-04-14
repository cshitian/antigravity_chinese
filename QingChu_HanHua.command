#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo
echo "[1/3] Detecting Antigravity process..."
osascript -e 'tell application "Antigravity" to quit' >/dev/null 2>&1 || true
pkill -f "Antigravity" >/dev/null 2>&1 || true
sleep 1

echo
echo "[2/3] Restoring Official Files..."
python3 "$SCRIPT_DIR/AntigravityHanHua_GongJu.py" --huifu "$@"
status=$?

echo
echo "[3/3] Restoration Complete!"
echo
echo "[Note] Antigravity has been restored to its original state."
echo
echo "Press Enter to exit..."
read -r _
exit $status
