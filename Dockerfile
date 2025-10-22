# Stage 1 — Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose port your Flask app runs on
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
