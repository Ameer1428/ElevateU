# # ============================
# # 1) Build Frontend (Vite)
# # ============================
# FROM node:20 AS frontend-builder

# WORKDIR /app/frontend

# COPY frontend/package.json frontend/package-lock.json ./
# RUN npm install

# COPY frontend/ .
# RUN npm run build


# # ============================
# # 2) Backend Image
# # ============================
# FROM python:3.10-slim

# WORKDIR /app

# # Install dependencies
# COPY backend/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy backend source
# COPY backend/ .

# # Copy built frontend into backend (to serve as static files)
# COPY --from=frontend-builder /app/frontend/dist ./static

# # Expose port
# EXPOSE 5000

# # Start backend (make sure app.py runs the backend)
# CMD ["python", "app.py"]

# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p agent static

# Copy .env file (if it exists)
COPY .env .env

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "app.py"]