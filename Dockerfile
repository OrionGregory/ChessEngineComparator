FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app/ChessApp

# Install system dependencies
RUN apt-get update && \
    apt-get install -y gcc libpq-dev redis-server && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY ChessApp/ .

# Collect static files (optional, if you use Django staticfiles)
# RUN python manage.py collectstatic --noinput

# Expose port for Django
EXPOSE 8000

# Start Redis server, Django, and Celery worker using supervisord
RUN pip install supervisor
COPY supervisord.conf /etc/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisord.conf"]