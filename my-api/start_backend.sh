#!/bin/bash

LOG_FILE="/home/jw2349/REVIEWER2/my-api/backend.log"
HOSTNAME_FILE="/home/jw2349/REVIEWER2/my-api/gpu_node.txt"

# Log the start time
echo "Starting backend setup at $(date)" >> $LOG_FILE

# Function to start the backend server inside a tmux session
start_tmux_session() {
    # Delete the existing GPU node record
    echo "Deleting the existing GPU node record" >> $LOG_FILE
    rm -f $HOSTNAME_FILE
    echo "Existing GPU node record deleted successfully" >> $LOG_FILE

    echo "Creating a new tmux session named backend_session" >> $LOG_FILE
    tmux new-session -d -s backend_session "srun --pty --gres=gpu:a6000:1 --mem 64000 -n 1 /bin/bash -c '
    # Record the GPU node hostname
    HOSTNAME=\$(hostname)
    echo \$HOSTNAME > $HOSTNAME_FILE
    echo \"Recorded GPU node hostname: \${HOSTNAME}\" >> $LOG_FILE
    echo \"GPU node hostname recorded successfully\" >> $LOG_FILE
    
    # Set up the reverse SSH tunnel
    echo \"Setting up reverse SSH tunnel\" >> $LOG_FILE
    ssh -f -N -R 3000:localhost:3000 jw2349@osmot.cs.cornell.edu
    echo \"Reverse SSH tunnel set up successfully\" >> $LOG_FILE
    
    # Set up the environment
    echo \"Setting up the environment\" >> $LOG_FILE
    source ~/.zshrc
    echo \"Environment set up successfully\" >> $LOG_FILE
    
    # Navigate to the backend directory
    echo \"Navigating to the backend directory\" >> $LOG_FILE
    cd /home/jw2349/REVIEWER2/my-api
    echo \"Navigated to the backend directory successfully\" >> $LOG_FILE
    
    # Start the backend server
    echo \"Starting the backend server\" >> $LOG_FILE
    python rvfastapi.py
    echo \"Backend server started successfully\" >> $LOG_FILE
    '"
    
    echo "Backend server and monitoring started in tmux session at $(date)" >> $LOG_FILE
}

# Check if the tmux session is already running
if [ -f $HOSTNAME_FILE ]; then
    GPU_NODE=$(cat $HOSTNAME_FILE)
    echo "Checking connection to GPU node: $GPU_NODE" >> $LOG_FILE
    ssh -o ConnectTimeout=10 $GPU_NODE "true"
    
    if [ $? -ne 0 ]; then
        echo "Unable to connect to GPU node $GPU_NODE. Starting a new session." >> $LOG_FILE
        start_tmux_session
    else
        echo "Successfully connected to GPU node $GPU_NODE. No need to restart." >> $LOG_FILE
    fi
else
    echo "No GPU node recorded. Starting a new session." >> $LOG_FILE
    start_tmux_session
fi
