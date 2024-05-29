# Use the python:3.9-slim base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to leverage Docker cache
COPY requirements.txt .

# Update pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch with CUDA support and other necessary dependencies
RUN pip install torch==2.3.0+cu118 torchvision==0.18.0+cu118 torchaudio==2.3.0+cu118 --extra-index-url https://download.pytorch.org/whl/cu118

# Install system dependencies and additional codecs for ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire app directory to the container
COPY app /app

# Expose port 5000 to the world outside this container
EXPOSE 5000

# Define the entry point to run the Flask app
CMD ["python", "/app/FE.py"]