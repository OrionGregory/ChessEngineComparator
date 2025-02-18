import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chessboard } from 'react-chessboard';
import { Chess } from 'chess.js';
import NavBar from "./components/NavBar";

const sessionId = "test_session";

function App() {
  const [fen, setFen] = useState("start");
  const [status, setStatus] = useState("");
  const [gameOver, setGameOver] = useState(false);
  const chess = new Chess(); //

  useEffect(() => {
    const interval = setInterval(fetchFEN, 100000);
    return () => clearInterval(interval);
  }, []);

  const fetchFEN = async () => {
    try {
      const response = await axios.get("http://localhost:5000/get_fen", {
        params: { session_id: sessionId }
      });
  
      if (response.data.fen) {
        setFen(response.data.fen);
        checkGameOver(response.data.fen);
      } else {
        console.error("Invalid response:", response.data);
      }
    } catch (error) {
      console.error("Error fetching FEN:", error.response ? error.response.data : error.message);
  
      // If session is missing, initialize a new game
      if (error.response && error.response.data.error === "Session not found") {
        console.warn("Session not found! Initializing new game...");
        await newGame();
      }
    }
  };

  const checkGameOver = (fen) => {
    chess.load(fen);
    if (chess.isGameOver()) {
      setGameOver(true);
      if (chess.isCheckmate()) {
        setStatus(chess.turn() === 'w' ? "Bot Won! 😞" : "You Won! 🎉");
      } else {
        setStatus("It's a Draw! 🤝");
      }
    }
  };

  const onDrop = async (sourceSquare, targetSquare) => {
    if (gameOver) return;

    const move = { from: sourceSquare, to: targetSquare, promotion: "q" };
    chess.load(fen);
    try {
      const result = chess.move(move);
      if (!result) {
        setStatus("Invalid move! Try again.");
        return;
      }

      setFen(chess.fen());
      setStatus("");

      await axios.post("http://localhost:5000/update_fen", {
        session_id: sessionId,
        fen: chess.fen(),
      });
    } catch (error) {
      setStatus("Invalid move! Try again.");
    }
  };

  const newGame = async () => {
    try {
      const response = await axios.post("http://localhost:5000/new_game", {
        session_id: sessionId,
      });

      if (response.data.success) {
        setFen(response.data.fen);
        setGameOver(false);
        setStatus("");
      }
    } catch (error) {
      console.error("Error starting a new game:", error);
    }
  };

  return (
    
    <div style={styles.container}>
      <NavBar />
      <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      padding: '20px' 
    }}></div>
      <h1 style={styles.title}>Play as White!</h1>
      <Chessboard position={fen} onPieceDrop={onDrop} boardWidth={600}
        customDarkSquareStyle={{ backgroundColor: '#779556' }}
        customLightSquareStyle={{ backgroundColor: '#edeed1' }}
      />
      <p style={styles.status}>{status}</p>
      <button style={styles.button} onClick={newGame}>New Game</button>
    </div>
  );
}

const styles = {
  container: {
    textAlign: 'center',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
    backgroundColor: '#f5f5f5',
    minHeight: '100vh',
  },
  title: {
    fontSize: '2rem',
    marginBottom: '20px',
  },
  status: {
    fontSize: '1.2rem',
    color: 'red',
    marginTop: '10px',
  },
  button: {
    marginTop: '15px',
    padding: '10px 20px',
    fontSize: '1rem',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
  },
};

export default App;