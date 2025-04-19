# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt --ignore-installed starkbank-ecdsa || \
    pip install --no-cache-dir --no-binary :all: starkbank-ecdsa==2.2.0 && \
    pip install --no-cache-dir -r requirements.txt --ignore-installed starkbank-ecdsa

# Command to run your script
CMD ["sh", "-c", "python notifications.py & python app.py"]
