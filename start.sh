#!/bin/bash
# Start the backend server
cd /app/backend
python -m app.main &
BACKEND_PID=$!

# Start the frontend server
cd /app/frontend
npm start &
FRONTEND_PID=$!

# Handle termination signals
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

# Keep the script running
wait 