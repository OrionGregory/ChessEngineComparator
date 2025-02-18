# Chess Web App

A web-based chess game where a bot plays against the user. The app is built with **React (frontend)** and **Flask (backend)**.

## Features

- Play chess against a bot
- Moves are updated in real-time
- Displays game over message (Checkmate/Draw)
- "New Game" button resets the board

---

## 🛠️ Local Setup Instructions

### **1. Install Backend (Flask) Dependencies**

Make sure you have **Python 3.8+** installed.

```sh
cd backend
pip install -r requirements.txt
```

#### **Required Python Packages**

- `flask`
- `flask-cors`
- `chess`
- `requests`

You can install them manually(as haven't included a requirements file):

```sh
pip install flask flask-cors chess requests
```

### **3. Run the Flask Backend**

```sh
python app.py
```

This will start the backend server on **http://localhost:5000**.

---

### **4. Install Frontend (React) Dependencies**

Make sure you have **Node.js (v16+)** installed.

```sh
cd frontend
npm install
```

### **5. Run the React Frontend**

```sh
npm start
```

This will start the frontend on **http://localhost:3000**.

---

### **6. Start the Chess Bot**

Run the bot script in another terminal:

```sh
python bot.py
```

This script polls the server for the latest move and plays as Black.

---

## 📜 License

This project is open-source and available under the **MIT License**.

---

Let me know if you need any modifications! 🚀
