#!/bin/bash
# Usage: ./multi_chaos.sh {start|stop|attach} <config_name>
# Example: ./multi_chaos.sh start server1.cfg

ACTION=$1
CFG=$2

if [ -z "$CFG" ]; then
    echo "Usage: $0 {start|stop|attach|status} <config_file>"
    exit 1
fi

SESSION="chaos_${CFG%.*}"

case "$ACTION" in
    start)
        screen -dmS "$SESSION" python3 chaos.py "$CFG"
        echo "[+] Started $SESSION using $CFG"
        ;;
    stop)
        screen -S "$SESSION" -X quit
        echo "[+] Stopped $SESSION"
        ;;
    attach)
        screen -r "$SESSION"
        ;;
    status)
        screen -ls | grep "$SESSION" && echo "Status: RUNNING" || echo "Status: STOPPED"
        ;;
esac