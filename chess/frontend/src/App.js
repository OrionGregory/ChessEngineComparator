import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Box, Typography, CircularProgress, Button } from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import BotUpload from "./components/BotUpload";
import ChessGame from "./components/ChessGame";
import Tournament from "./components/Tournament";
import Auth from "./components/Auth";

function App() {
  const [file, setFile] = useState(null);
  const [game, setGame] = useState({
    position: 'start',
    filename: null,
    gameOver: false,
    result: null
  });
  const [tournamentLogs, setTournamentLogs] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        const response = await axios.get("https://localhost:5000/auth/status", { withCredentials: true });

        if (response.status === 200 && response.data.authenticated) {
          setIsAuthenticated(true);
          setUserData(response.data.user);
        }
      } catch (error) {
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthentication();
  }, []);

  const handleLogout = async () => {
    try {
      await axios.get("https://localhost:5000/auth/logout", { withCredentials: true });
      setIsAuthenticated(false);
      setUserData(null);
      window.location.reload();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

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
      const response = await axios.post("https://localhost:5000/upload", formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        withCredentials: true,
      });

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
      alert("Upload failed: " + (error.response?.data?.error || error.message));
    }
  };

  const onDrop = async (sourceSquare, targetSquare) => {
    if (game.gameOver) {
      alert("Game is already over!");
      return;
    }

    try {
      const response = await axios.post("https://localhost:5000/make_move", {
        filename: game.filename,
        user_move: `${sourceSquare}${targetSquare}`,
      });

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
        alert("Invalid move! Try again.");
      }
    } catch (error) {
      console.error("Move failed", error);
    }
  };

  const removeBot = async () => {
    if (!game.filename) {
      alert("No bot is currently loaded");
      return;
    }
  
    console.log("Attempting to remove bot:", game.filename); // Debugging log
  
    try {
      const response = await axios.post(
        "https://localhost:5000/remove_bot",
        { filename: game.filename },
        { withCredentials: true } // Ensure credentials are sent
      );
  
      if (response.data.success) {
        setGame({
          position: 'start',
          filename: null,
          gameOver: false,
          result: null
        });
        alert("Bot removed successfully");
      } else {
        alert("Failed to remove bot: " + response.data.error);
      }
    } catch (error) {
      alert("Failed to remove bot: " + (error.response?.data?.error || error.message));
    }
  };

  const runTournament = async () => {
    setIsLoading(true);
    setTournamentLogs('Starting tournament...\n');

    try {
      const response = await axios.get("https://localhost:5000/run_tournament", {
        withCredentials: true, // Ensure credentials are sent
      });
      const data = response.data;

      setTournamentLogs(`=== Tournament Execution ===\n${data.output}\nTournament completed successfully\n`);
    } catch (error) {
      setTournamentLogs('Tournament Execution Failed\n' + (error.response?.data?.error || error.message));
      alert("Failed to run tournament.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return isAuthenticated ? (
    <div className="App">
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
          <Typography variant="h3" gutterBottom>Chess Bot Arena</Typography>
          <Button
            variant="contained"
            color="secondary"
            onClick={handleLogout}
            startIcon={<LogoutIcon />}
            sx={{ alignSelf: 'flex-end', mb: 2 }}
          >
            Logout
          </Button>
          <BotUpload handleFileChange={handleFileChange} uploadFile={uploadFile} file={file} isAuthenticated={isAuthenticated}/>
          <ChessGame game={game} onDrop={onDrop} removeBot={removeBot} />
          <Tournament runTournament={runTournament} isLoading={isLoading} tournamentLogs={tournamentLogs} />
        </Box>
      </Container>
    </div>
  ) : (
    <Auth />
  );
}

export default App;