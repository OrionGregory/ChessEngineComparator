FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV NODE_VERSION 18.x

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y gcc libpq-dev redis-server curl gnupg && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js for React frontend
RUN curl -sL https://deb.nodesource.com/setup_${NODE_VERSION} | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Copy Django project files
COPY django-template/ /app/django-template/

# Install Python dependencies
WORKDIR /app/django-template
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy and build React frontend
COPY django-template/frontend/ /app/django-template/frontend/
WORKDIR /app/django-template/frontend
RUN npm install && npm run build

# Move back to Django directory
WORKDIR /app/django-template

# Install supervisor for process management
RUN pip install supervisor
COPY supervisord.conf /etc/supervisord.conf

# Expose ports for Django and React
EXPOSE 8000 3000

CMD ["supervisord", "-c", "/etc/supervisord.conf"]