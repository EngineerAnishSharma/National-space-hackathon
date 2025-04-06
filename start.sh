#!/bin/sh
# Start the backend
cd /app/backend
python -m app.main &
BACKEND_PID=$!

# Start the frontend
cd /app/frontend
npm run start &
FRONTEND_PID=$!

# Handle termination properly
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

# Wait for processes to finish
wait 