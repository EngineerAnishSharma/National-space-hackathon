FROM python:3.11-slim

# Install Node.js
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install backend requirements
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy and install frontend requirements
COPY frontend/package*.json /app/frontend/
WORKDIR /app/frontend
RUN npm install

# Copy the rest of the application
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY start.sh /app/

# Build frontend (production build)
WORKDIR /app/frontend
RUN npm run build

# Make the startup script executable
WORKDIR /app
RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 8000 3000

# Run the application
CMD ["/app/start.sh"]

