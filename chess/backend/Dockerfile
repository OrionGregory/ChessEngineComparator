FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy backend files explicitly
COPY chess/backend/ /app/

# Copy SSL files explicitly from root (they are at the project root!)
COPY cert.pem /app/cert.pem
COPY key.pem /app/key.pem

# Copy Stockfish explicitly from root
COPY stockfish/stockfish-ubuntu-x86-64-avx2 /app/stockfish/stockfish-ubuntu-x86-64-avx2

# Ensure entrypoint.sh is executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]
