import React, { useState } from 'react';
import axios from 'axios';
import { Chessboard } from 'react-chessboard';
import NavBar from "./components/NavBar";

function App() {
  const [file, setFile] = useState(null);
  const [game, setGame] = useState({ 
    position: 'start', 
    filename: null,
    gameOver: false,
    result: null
  });
  
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const uploadFile = async () => {
    if (!file) {
      alert("Please select a file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:5000/upload", formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      console.log("Upload response:", response.data);
      
      if (response.data.filename) {
        setGame({ 
          position: response.data.initial_fen, 
          filename: response.data.filename,
          gameOver: false,
          result: null
        });
        alert("File uploaded successfully");
      } else {
        alert("Upload failed: No filename returned");
      }
    } catch (error) {
      console.error("Upload failed", error);
      alert("Upload failed: " + (error.response?.data?.error || error.message));
    }
  };

  const onDrop = async (sourceSquare, targetSquare) => {
    if (game.gameOver) {
      alert("Game is already over!");
      return;
    }

    const move = `${sourceSquare}${targetSquare}`;
    console.log(`Attempting move: ${move}`);
    console.log(`Current game state:`, game);

    try {
      const response = await axios.post("http://localhost:5000/make_move", {
        filename: game.filename,
        user_move: move,
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log("Server response:", response.data);

      if (response.data.valid) {
        setGame({
          ...game,
          position: response.data.fen,
          gameOver: response.data.game_over || false,
          result: response.data.result || null
        });

        if (response.data.game_over) {
          alert(`Game Over! Result: ${response.data.result}`);
        }
      } else {
        console.warn("Invalid move details:", response.data);
        alert("Invalid move! Try again.");
      }
    } catch (error) {
      console.error("Move failed", error.response ? error.response.data : error);
    }
  };

  return (
    <div className="App">
      <NavBar />
      <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      padding: '20px' 
    }}>
      <h1>Chess Bot Arena</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <input 
          type="file" 
          onChange={handleFileChange} 
          accept=".py"
        />
        <button onClick={uploadFile}>Upload Bot</button>
      </div>

      {game.filename && (
        <div style={{ marginBottom: '20px' }}>
          <p>Current Bot: {game.filename}</p>
          {game.gameOver && (
            <p style={{ color: 'red', fontWeight: 'bold' }}>
              Game Over! Result: {game.result}
            </p>
          )}
        </div>
      )}

      <Chessboard 
        position={game.position} 
        onPieceDrop={onDrop} 
        boardWidth={600}
        customDarkSquareStyle={{ backgroundColor: '#779556' }}
        customLightSquareStyle={{ backgroundColor: '#edeed1' }}
      />
    </div>
    </div>
  );
}

export default App;