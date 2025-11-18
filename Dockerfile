# ---------- FRONTEND BUILD ----------
FROM node:18 AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend ./
RUN npm run build


# ---------- BACKEND IMAGE ----------
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for Python, Mongo, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend/ ./backend/
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy React build into Flask static folder
RUN mkdir -p backend/static
COPY --from=frontend-build /app/frontend/dist/ ./backend/static/

# Expose port
EXPOSE 5000

WORKDIR /app/backend
CMD ["python", "app.py"]
