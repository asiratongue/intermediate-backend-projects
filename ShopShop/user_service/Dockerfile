# Use the official Python image from the Docker Hub
FROM python:3.11-slim as builder

# Set the working directory in the container
WORKDIR /app

ENV PYTHONPATH=/app
# Copy the current directory contents into the container at /app
COPY . /app

# install the image
RUN apt-get update && \
apt-get install -y --no-install-recommends build-essential python3-dev && \
pip install --no-cache-dir --upgrade pip setuptools wheel && \
pip install --no-cache-dir -r requirements.txt && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["gunicorn", "user_service.wsgi:application", "--bind", "0.0.0.0:8000"]


