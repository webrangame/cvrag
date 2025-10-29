FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY *.sql ./

# Create necessary directories
RUN mkdir -p data documents chroma_db

# Expose port
EXPOSE 8000

# Run the application
CMD streamlit run app.py --server.port 8000 --server.address 0.0.0.0

