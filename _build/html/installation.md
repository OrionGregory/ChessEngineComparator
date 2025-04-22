# Quick Start (Recommended)

The easiest way to build, run, and develop this project is with Docker and Docker Compose. All dependencies (Python, Postgres, Redis, Celery, Django, etc.) are managed for you.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 1. Clone the repository

```bash
git clone https://github.com/yourusername/ChessEngineComparator.git
cd ChessEngineComparator
```

## 2. Configure environment variables

Copy `.env.example` to `.env` and edit as needed (database password, etc.).
```
DJANGO_SECRET_KEY="django-secure-key-for-your-app"
DB_PASSWORD="password"
GOOGLE_CLIENT_ID="client_id"
GOOGLE_CLIENT_SECRET="secret"
REDIRECT_URI="https://localhost:5000/auth/callback"
DB_HOST="ip"
DB_PORT="port#"
DB_NAME="DBname"
DB_USER="DBuser"
```

## 3. Build and start all services

```bash
docker-compose up --build
```

- This will:
  - Build the Django app image
  - Start Postgres, Redis, Django, Celery, and Supervisor
  - Expose the web app at [http://localhost:8000](http://localhost:8000)

## 4. Run migrations and create a superuser

In a new terminal:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## 5. Access the app

- Web: [http://localhost:8000](http://localhost:8000)
- Admin: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## Customization

- **Change database:** Edit `.env` and `docker-compose.yml`, then restart.
- **Change Celery config:** Edit `supervisord.conf` or Django settings, then rebuild/restart.

---
## Adding a New OAuth Provider to the Django App

This guide walks you through the steps to integrate a new social login provider (e.g., Google, GitHub, Facebook) using Django Allauth.

## Prerequisites

- The Django application must already include `django-allauth` and be running.
- You must have superuser access to the Django admin panel.
- The provider (e.g., Google) must have OAuth credentials set up in its developer console.

---

### 1. Access the Admin Panel

Navigate to the admin interface:
http://localhost:8000/admin

Log in using your superuser credentials.

---

### 2. Create a New Social Application

In the admin panel:

1. Go to **Social Accounts** → **Social Applications**.
2. Click **Add Social Application**.
3. Choose your desired **Provider** (e.g., Google).
4. Fill out the form:

   - **Name**: A descriptive name for your app (e.g., `Google Login`).
   - **Client ID** and **Secret Key**: Obtain these from the provider’s developer dashboard.
   - **Key**: Usually optional.
   - **Sites**: Select `example.com` or `localhost`.
     -  If localhost is not available on Sites, you will need to add it in the Sites panel

Click **Save**.

---

### 3. Update Environment Variables

Open your `.env` file and add the following (adjust for your provider):


## Manual/Advanced Usage

If you want to run services outside Docker (for development or debugging), see [docs/manual.md](docs/manual.md).

# External Resources
A Google Cloud SQL PostgreSQL database was used, this was payed, and we used the lowest tier, which offered 1 CPU and 612MB of RAM. 

# FAQ (Frequently Asked Questions)
Issues
---
