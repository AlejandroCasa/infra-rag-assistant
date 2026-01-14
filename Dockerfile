# Use the official lightweight Python 3.13 image
FROM python:3.13-slim

# Prevent Python from writing .pyc files and force real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
# - build-essential: for compiling some python packages
# - curl: for the healthcheck
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# --- OPTIMIZATION: CPU-ONLY PYTORCH ---
# We install PyTorch explicitly from the CPU index URL to avoid downloading 
# massive CUDA (GPU) drivers. This reduces image size by ~4GB.
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install the rest of the dependencies
# Pip will skip 'torch' here as it's already satisfied by the step above
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY . .

# Make the entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# Expose the Streamlit port
EXPOSE 8501

# Healthcheck to ensure the container is ready
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Define the entrypoint script (handles auto-ingestion)
ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]