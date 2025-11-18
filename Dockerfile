# ============================
# 1) Build Frontend (Vite)
# ============================
FROM node:18 AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend/ .
RUN npm run build


# ============================
# 2) Backend Image
# ============================
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy built frontend into backend (to serve as static files)
COPY --from=frontend-builder /app/frontend/dist ./static

# Expose port
EXPOSE 5000

# Start backend (make sure app.py runs the backend)
CMD ["python", "app.py"]
