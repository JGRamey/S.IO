# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment variables to prevent Python from writing .pyc files and to buffer output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system-level dependencies
# We need postgresql-client for database connectivity checks and build-essential for compiling some Python packages.
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container to leverage Docker's build cache
COPY config/requirements.txt .
COPY config/pyproject.toml .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Set proper permissions
RUN chmod +x /app/yggdrasil/ || true

# Expose ports for the application
EXPOSE 8000 5431
## Changed to 5431 from 5432 - If this causes problems we can change it back to 5432 
## Make sure the other docker files are using 5431:5431 first before changing back

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - can be overridden by docker-compose
CMD ["python", "-m", "yggdrasil.api.main"]