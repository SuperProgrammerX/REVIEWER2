#!/bin/bash

# Change to the project directory
cd /home/jw2349/REVIEWER2/chat-app

# Start the React frontend using pm2 with nohup
nohup pm2 start npm --name "react-frontend" -- start > frontend_pm2.log 2>&1 &
