#!/bin/bash

# Check if the server is running
if ! pgrep -f "uvicorn rvfastapi:app" > /dev/null
then
    echo "Server is not running. Restarting..."
    ./start_server.sh
else
    echo "Server is running."
fi
