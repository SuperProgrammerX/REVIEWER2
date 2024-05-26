#!/bin/bash
source /home/jw2349/.conda/envs/myenv/bin/activate  # Activate virtual environment
uvicorn rvfastapi:app --host 0.0.0.0 --port 3001 --log-level debug
