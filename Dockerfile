# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /backend

# Install system dependencies (including PortAudio)
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only the necessary files from the backend directory
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
COPY backend/ .  

# Set environment variables (optional, adjust as needed)
ENV PYTHONUNBUFFERED=1

# Command to run your Flask app (adjust based on your app's entry point)
CMD ["python", "app.py"]
