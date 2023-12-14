#!/bin/bash

# Path to the server executable
SERVER_CMD="/llama.cpp/server -m /models/yi-34b-chat.Q5_K_M.gguf -c 4096 -ngl 50 -nommq -t 5"

# File to store the server's process ID
PID_FILE="server.pid"

start_server() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null; then
            echo "Server is already running with PID $PID."
            return
        fi
    fi

    echo "Starting server..."
    nohup $SERVER_CMD > server.log 2>&1 &
    echo $! > $PID_FILE
    echo "Server started with PID $(cat $PID_FILE), waiting for initialization..."
    sleep 20
    echo "Server initialization complete."
}

stop_server() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null; then
            echo "Stopping server with PID $PID..."
            kill $PID
            rm $PID_FILE
            echo "Server stopped."
        else
            echo "No running server found with PID $PID."
            rm $PID_FILE
        fi
    else
        echo "Server is not running."
    fi
}

case $1 in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac