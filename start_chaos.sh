#!/bin/bash

# Configuration
SESSION_NAME="mbii_chaos"
PYTHON_SCRIPT="chaos.py"
PYTHON_BIN="python3"

start() {
    screen -ls | grep -q "$SESSION_NAME"
    if [ $? -eq 0 ]; then
        echo "[!] Chaos is already running in screen session: $SESSION_NAME"
    else
        echo "[*] Starting Chaos in detached mode..."
        screen -dmS "$SESSION_NAME" $PYTHON_BIN $PYTHON_SCRIPT
        echo "[+] Chaos started. Use './manage_chaos.sh attach' to view logs."
    fi
}

stop() {
    screen -ls | grep -q "$SESSION_NAME"
    if [ $? -eq 0 ]; then
        echo "[*] Stopping Chaos session..."
        screen -S "$SESSION_NAME" -X quit
        echo "[+] Chaos stopped."
    else
        echo "[!] Chaos is not running."
    fi
}

restart() {
    echo "[*] Restarting Chaos..."
    stop
    sleep 1
    start
}

attach() {
    echo "[*] Attaching to Chaos console... (Press Ctrl+A then D to detach)"
    screen -r "$SESSION_NAME"
}

status() {
    screen -ls | grep -q "$SESSION_NAME"
    if [ $? -eq 0 ]; then
        echo "[+] Chaos Status: RUNNING"
    else
        echo "[-] Chaos Status: STOPPED"
    fi
}

case "$1" in
    start) start ;;
    stop) stop ;;
    restart) restart ;;
    attach) attach ;;
    status) status ;;
    *) echo "Usage: $0 {start|stop|restart|attach|status}" ;;
esac