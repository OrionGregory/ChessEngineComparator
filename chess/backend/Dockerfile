FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create stockfish directory
RUN mkdir -p /app/stockfish

# Copy requirements file
COPY chess/backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Stockfish binary from host to container
# The binary is at the root of the project
COPY stockfish/stockfish-ubuntu-x86-64-avx2 /app/stockfish/stockfish

# Make sure the binary is executable
RUN chmod +x /app/stockfish/stockfish

# Copy the rest of the application
COPY chess/backend/ .

# Create uploads directory if it doesn't exist
RUN mkdir -p uploads

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV STOCKFISH_PATH=/app/stockfish/stockfish

# Expose port
EXPOSE 5000

# Add a simple test script to verify Stockfish works
RUN echo '#!/bin/bash\necho "Testing Stockfish..."\nif [ -f "$STOCKFISH_PATH" ]; then\n  echo "Stockfish found at $STOCKFISH_PATH"\n  $STOCKFISH_PATH --help | head -n 3\n  echo "Stockfish test complete"\nelse\n  echo "ERROR: Stockfish not found at $STOCKFISH_PATH"\n  exit 1\nfi' > /app/test_stockfish.sh && \
    chmod +x /app/test_stockfish.sh

# Command to run the application
CMD ["/bin/bash", "-c", "./test_stockfish.sh && python app.py"]