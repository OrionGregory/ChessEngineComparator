# PostgreSQL Setup for Local Testing of Users

## 1. Installing PostgreSQL

1. **Download PostgreSQL:**  
   Visit the [PostgreSQL Downloads](https://www.postgresql.org/download/) page and follow the installation instructions for your operating system (Windows, macOS, or Linux).
   Use the SQL Shell Terminal from here on out

2. **Verify Installation:**  
   Open a terminal and run:
   ```bash
   psql --version
   ```

## Setting Up the Database
```bash 
psql -U postgres
```

```sql
CREATE DATABASE chess_app;
\c chess_app;
```

```sql
CREATE USER chess_user WITH PASSWORD 'password';
```

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL
);
```

```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chess_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO chess_user;
```

## Create a .env File
Everything is local right now, so this doesn't really matter, but I'm including it nonetheless. 
```bash
pip install python-dotenv
```
Create .env file in root directory  
```ini
JWT_SECRET_KEY=<key>
DATABASE_URL=<url>
```
Do not push this .env file. It's already gitignored, so that shouldn't be a problem. 

## Run Time User Creation/Login
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "email": "testemail", "password": "password123"}'
```
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "password123"}'
```

## Upload File
Use the token that you get back after logging in for `YOUR_JWT_TOKEN_HERE`
```bash
curl -X POST http://localhost:5000/upload_file \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -F "file=@/path/to/your/file.txt"
```

## My Files
Use the token that you get back after logging in for `YOUR_JWT_TOKEN_HERE`
```bash 
curl -X GET http://localhost:5000/my_files \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```
FOR OAUTH YOU NEED TO ADD THE FOLLOWING TO THE USERS TABLE
```
ALTER TABLE users 
ADD COLUMN oauth_provider VARCHAR(50),
ADD COLUMN oauth_id VARCHAR(255);
```

## Run File as Bot
`I don't know if this works because I'm having stockfish pathing problems`  

Use the token that you get back after logging in for `YOUR_JWT_TOKEN_HERE`
```bash
curl -X POST http://localhost:5000/run_bot_command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{"file_id": YOUR_FILE_ID}'
```


## Docker 

Make a docker account and verify your email.  

Make sure you copy and paste your cert.pem and key.pem into your root folder.   

Docker requires linux path for stockfish. Have this stockfish folder in your root folder. 

Run in git bash terminal: 
```bash
chmod +x ./chess/backend/entrypoint.sh
dos2unix chess/backend/entrypoint.sh
```


```bash
ChessEngineComparator/
├── chess/
│   ├── backend/
│   │   ├── app.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── Dockerfile
│   │   ├── extensions.py
│   │   ├── models.py
│   │   ├── uploads/
│   │   │   └── Test.py
│   │   └── ...
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── App.js
│   │   │   ├── components/
│   │   │   │   └── BotUpload.js
│   │   │   └── ...
│   │   ├── Dockerfile
│   │   └── ...
├── stockfish/
│   ├── stockfish-ubuntu-x86-64-avx2
├── cert.pem
├── key.pem
├── requirements.txt
├── docker-compose.yml
├── entrypoint.sh
└── .env
```