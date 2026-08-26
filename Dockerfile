# Multi-stage build for Phantom Folders
# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --production=false
COPY src/ src/
COPY index.html vite.config.mjs ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.12-slim
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ backend/
COPY main.py .

# Copy pre-built frontend from stage 1
COPY --from=frontend-builder /app/dist dist/

# Create storage directory
RUN mkdir -p /data/phantom_vault

# Environment
ENV PHANTOM_STORAGE_DIR=/data/phantom_vault
ENV PHANTOM_HOST=0.0.0.0
ENV PHANTOM_PORT=8000

EXPOSE 8000

CMD ["python", "main.py", "--server", "--host", "0.0.0.0", "--port", "8000"]
