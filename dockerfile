FROM python:3.11-slim

# Install Node.js
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application files
COPY frontend/ /app/frontend/
COPY backend/ /app/backend/

# Install backend dependencies
WORKDIR /app/backend
RUN pip install -r requirements.txt

# Install frontend dependencies
WORKDIR /app/frontend
RUN npm i --legacy-peer-deps
RUN npm run build

# Create startup script
WORKDIR /app
RUN echo '#!/bin/sh\ncd /app/backend && python -m app.main & \ncd /app/frontend && npm run start\nwait' > /app/start.sh && \
    chmod +x /app/start.sh

# Expose ports
EXPOSE 8000 3000

# Run both services
CMD ["/app/start.sh"]

