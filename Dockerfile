# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install additional dependencies for hiRAG that do not change often
RUN pip install --no-cache-dir \
    nano-vectordb \
    chromadb \
    qdrant-client \
    weaviate-client

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src/

# Create a default .env file (environment variables will come from Docker Compose)
RUN echo "# Environment variables provided by Docker Compose" > .env

# Create data and logs directories
RUN mkdir -p /app/data /app/logs

# Set Python path
ENV PYTHONPATH=/app/src

# Expose port for MCP server
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Command to run the MCP server
CMD ["python", "src/crawl4ai_mcp.py"]