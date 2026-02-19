FROM python:3.10-slim

# Install system dependencies needed for llama-cpp-python
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies first
RUN pip install fastapi uvicorn llama-cpp-python

# Copy server file and menu
COPY server.py /app/
COPY menu.json /app/

# Create models directory and copy the specific model file
RUN mkdir -p /app/models

# Expose port
EXPOSE 8000

# Run your server.py file
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]