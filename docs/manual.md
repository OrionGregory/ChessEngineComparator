# Running the Django Web Application with Celery Backend (Without Docker)

This guide explains how to set up and run the Django web application and Celery backend without using Docker.

---

## Prerequisites

Before proceeding, ensure you have the following installed on your system:

1. **Python 3.11 or higher**  
   [Download Python](https://www.python.org/downloads/)

2. **PostgreSQL**  
   [Install PostgreSQL](https://www.postgresql.org/download/)

3. **Redis**  
   [Install Redis](https://redis.io/docs/getting-started/installation/)

4. **Virtual Environment (Optional but Recommended)**  
   [Python Virtual Environment Guide](https://docs.python.org/3/tutorial/venv.html)

---

## Step 1: Clone the Repository

Clone the project repository to your local machine:


git clone https://github.com/yourusername/ChessEngineComparator.git
cd ChessEngineComparator


## Step 2: Set Up Environment Variables
Copy the .env.example file to .env:

Edit the .env file to configure your database, Redis, and other settings:

---

## Step 3: Set Up the Python Environment

1. Create a virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate
```
2. Install Python Requirements
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Set Up the Database
Start PostgreSQL and create a database:
1. Start PostgreSQL and create a db
```bash
psql -U postgres
CREATE DATABASE your_database_name;
CREATE USER your_database_user WITH PASSWORD 'your_database_password';
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_database_user;
```
2. Run Django Migrations:
```bash
python ChessApp/manage.py migrate
```
3. Create a superuser for the Django admin panel:
```bash
python ChessApp/manage.py createsuperuser
```

## Step 5: Start Redis
```bash
redis-server
```

If this doesn't work because redis is not installed, please use 
```bash
sudo apt install redis
```
## Step 6: Run the Celery Worker
In a new terminal, activate your virtual environment (if applicable) and start the Celery worker:
```bash
cd ChessApp
celery -A web_django worker --loglevel=info
```

## Step 7: Run the Django Development Server
In another terminal, activate your virtual environment (if applicable) and start the Django server:
```bash
python manage.py runserver
```
The application will be available at http://localhost:8000.

## Step 8: Access the Admin Panel
Navigate to the admin interface at http://localhost:8000/admin and log in using the superuser credentials you created earlier.

Notes
Static Files: If you need to collect static files, run:
```bash
python ChessApp/manage.py collectstatic
```
Media Files: Ensure the MEDIA_ROOT directory exists and has the correct permissions. You can initialize media directories using the provided management command:
```bash
python ChessApp/manage.py init_media_dirs
```
Celery Configuration: The Celery broker and result backend are configured to use Redis. Ensure the CELERY_BROKER_URL and CELERY_RESULT_BACKEND in settings.py match your Redis setup.

# Troubleshooting
Database Connection Issues: Ensure PostgreSQL is running and the credentials in .env are correct.
Redis Connection Issues: Verify that Redis is running and accessible on the default port (6379).
Missing Dependencies: Run pip install -r ChessApp/requirements.txt to ensure all dependencies are installed.
For further assistance, refer to the Django documentation or the Celery documentation.