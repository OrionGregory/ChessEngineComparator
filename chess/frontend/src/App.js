import React, { useState } from 'react';
import axios from 'axios';
import { Chessboard } from 'react-chessboard';
import NavBar from "./components/NavBar";
import {
  Container,
  Typography,
  Button,
  Box,
  Paper,
  Input,
  CircularProgress
} from '@mui/material';
import { CloudUpload, Delete } from '@mui/icons-material';

function App() {
  const [file, setFile] = useState(null);
  const [game, setGame] = useState({ 
    position: 'start', 
    filename: null,
    gameOver: false,
    result: null
  });
  const [tournamentLogs, setTournamentLogs] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
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

  const removeBot = async () => {
    if (!game.filename) {
      alert("No bot is currently loaded");
      return;
    }

    try {
      const response = await axios.post("http://localhost:5000/remove_bot", {
        filename: game.filename
      });

      if (response.data.success) {
        setGame({ 
          position: 'start', 
          filename: null,
          gameOver: false,
          result: null
        });
        alert("Bot removed successfully");
      }
    } catch (error) {
      console.error("Failed to remove bot:", error);
      alert("Failed to remove bot: " + (error.response?.data?.error || error.message));
    }
  };

  const runTournament = async () => {
    setIsLoading(true);
    setTournamentLogs('Starting tournament...\n');
    try {
        const response = await axios.get("http://localhost:5000/run_tournament");
        const data = response.data;
        
        let logContent = '';
        if (data.status === 'completed') {
            logContent = `=== Tournament Execution ===\n`;
            logContent += `Started at: ${data.timestamp}\n`;
            logContent += `${'-'.repeat(50)}\n\n`;
            logContent += data.output;
            logContent += `\n${'-'.repeat(50)}\n`;
            logContent += `Tournament completed successfully\n`;
        }
        
        setTournamentLogs(logContent);
    } catch (error) {
        console.error("Tournament failed:", error);
        let errorMessage = 'Tournament Execution Failed\n';
        errorMessage += '-'.repeat(50) + '\n';
        errorMessage += `Error: ${error.response?.data?.error || error.message}\n\n`;
        
        if (error.response?.data?.traceback) {
            errorMessage += 'Detailed Error:\n';
            errorMessage += error.response.data.traceback;
        }
        
        setTournamentLogs(errorMessage);
        alert("Failed to run tournament. Check the logs for details.");
    } finally {
        setIsLoading(false);
    }
};

  return (
    <div className="App">
      <NavBar />
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
          <Typography variant="h3" gutterBottom>
            Chess Bot Arena
          </Typography>
          
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Input
                type="file"
                onChange={handleFileChange}
                accept=".py"
                sx={{ display: 'none' }}
                id="bot-upload"
              />
              <label htmlFor="bot-upload">
                <Button
                  variant="contained"
                  component="span"
                  startIcon={<CloudUpload />}
                >
                  Choose Bot File
                </Button>
              </label>
              <Button
                variant="contained"
                color="primary"
                onClick={uploadFile}
                disabled={!file}
              >
                Upload Bot
              </Button>
            </Box>
          </Paper>

          {game.filename && (
            <Paper elevation={3} sx={{ p: 2, mb: 3, width: '100%', maxWidth: 600 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography>Current Bot: {game.filename}</Typography>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={removeBot}
                  startIcon={<Delete />}
                >
                  Remove Bot
                </Button>
              </Box>
              {game.gameOver && (
                <Typography color="error" sx={{ mt: 1, fontWeight: 'bold' }}>
                  Game Over! Result: {game.result}
                </Typography>
              )}
            </Paper>
          )}

          <Box sx={{ width: '100%', maxWidth: 600 }}>
            <Chessboard
              position={game.position}
              onPieceDrop={onDrop}
              boardWidth={600}
              customDarkSquareStyle={{ backgroundColor: '#779556' }}
              customLightSquareStyle={{ backgroundColor: '#edeed1' }}
            />
          </Box>

          {/* Tournament Section */}
          <Paper 
            elevation={3} 
            sx={{ 
              mt: 4,
              width: '100%', 
              maxWidth: 800,
              mx: 'auto',
              p: 2 
            }}
          >
            <Typography variant="h5" gutterBottom>
              Tournament Results
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={runTournament}
              disabled={isLoading}
              sx={{ mb: 2 }}
            >
              Run Tournament
            </Button>
            
            {isLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                <CircularProgress />
              </Box>
            ) : (
              <Paper
                sx={{
                  backgroundColor: '#f5f5f5',
                  p: 2,
                  maxHeight: '400px',
                  overflowY: 'auto',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  fontSize: '0.9em'
                }}
              >
                {tournamentLogs || 'Click "Run Tournament" to see results'}
              </Paper>
            )}
          </Paper>
        </Box>
      </Container>
    </div>
  );
}

export default App;