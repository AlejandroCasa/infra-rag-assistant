# Use python:3.13-slim as base
FROM python:3.13-slim

# Avoid Python from writing .pyc files and force stdout/stderr to be unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working directory inside the container
WORKDIR /app

# Installing system dependencies for building some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code of the application
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Healthcheck for checking if the app is alive
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Command to start the application
ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]