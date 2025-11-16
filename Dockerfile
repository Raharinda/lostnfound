# Base image Python
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps (optional)
RUN apt-get update && apt-get install -y curl && apt-get clean

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole project
COPY . .

# Expose the port Fly will route traffic to
EXPOSE 8080

# Run Flask App
CMD ["python", "app.py"]
