# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the requirements file from the root directory
COPY ../../requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY chess/backend /app/

# Copy SSL certificate files from the root directory
COPY ../../cert.pem /app/cert.pem
COPY ../../key.pem /app/key.pem

# Copy Stockfish executable
COPY ../../stockfish/stockfish-ubuntu-x86-64-avx2 /app/stockfish/stockfish-ubuntu-x86-64-avx2

# Copy the entrypoint script from the root directory
COPY chess/backend/entrypoint.sh /app/entrypoint.sh

# Verify that the SSL certificate files, Stockfish executable, and entrypoint script are copied correctly
RUN ls -l /app/cert.pem /app/key.pem /app/stockfish/stockfish-ubuntu-x86-64-avx2 /app/entrypoint.sh

# Expose the port the app runs on
EXPOSE 5000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]