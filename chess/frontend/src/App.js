import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Box, Typography, CircularProgress } from '@mui/material';

// Debug all imports
import BotUpload from "./components/BotUpload";
import Tournament from "./components/Tournament";
import Auth from "./components/Auth";
// Change the import to use a different name to avoid any possible naming conflicts
import NavbarComponent from "./components/Navbar";

// Log the types of all imported components
console.log('Imported components types:', {
  BotUpload: typeof BotUpload,
  Tournament: typeof Tournament,
  Auth: typeof Auth,
  NavbarComponent: typeof NavbarComponent
});

// Add a simple fallback component
const FallbackComponent = ({ name }) => (
  <div style={{ 
    border: '2px solid red', 
    padding: '20px', 
    margin: '10px', 
    background: '#ffeeee'
  }}>
    Error loading {name} component
  </div>
);

function App() {
  const [file, setFile] = useState(null);
  const [tournamentLogs, setTournamentLogs] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    console.log("App component mounted");
    const checkAuthentication = async () => {
      try {
        console.log("Checking authentication status...");
        const response = await axios.get("https://localhost:5000/auth/status", { withCredentials: true });

        console.log("Auth response:", response.data);
        if (response.status === 200 && response.data.authenticated) {
          setIsAuthenticated(true);
          setUserData(response.data.user);
          console.log("User authenticated:", response.data.user);
        }
      } catch (error) {
        console.error("Authentication check failed:", error);
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
        alert("Bot uploaded successfully");
      } else {
        alert("Upload failed: No filename returned");
      }
    } catch (error) {
      alert("Upload failed: " + (error.response?.data?.error || error.message));
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

  // Add debugging log before render
  console.log("Rendering App with auth state:", isAuthenticated);
  console.log("User data:", userData);

  // Don't render anything if there are import issues
  if (typeof NavbarComponent !== 'function' || typeof Auth !== 'function' ||
      typeof BotUpload !== 'function' || typeof Tournament !== 'function') {
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        <h2>Component Import Error</h2>
        <p>One or more components failed to import correctly:</p>
        <ul>
          <li>Navbar: {typeof NavbarComponent}</li>
          <li>Auth: {typeof Auth}</li>
          <li>BotUpload: {typeof BotUpload}</li>
          <li>Tournament: {typeof Tournament}</li>
        </ul>
        <p>Please check your component exports and imports.</p>
      </div>
    );
  }

  return (
    <div className="App" style={{ width: '100%', marginTop: '64px' }}>
      {typeof NavbarComponent === 'function' ? (
        <NavbarComponent 
          isAuthenticated={isAuthenticated} 
          userData={userData} 
          handleLogout={handleLogout} 
        />
      ) : (
        <FallbackComponent name="Navbar" />
      )}
      
      {isLoading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="calc(100vh - 64px)">
          <CircularProgress />
        </Box>
      ) : (
        <div style={{ width: '100%' }}>
          {isAuthenticated ? (
            <Container maxWidth="lg">
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
                <Typography variant="h3" gutterBottom>Chess Bot Arena</Typography>
                {typeof BotUpload === 'function' ? (
                  <BotUpload 
                    handleFileChange={handleFileChange} 
                    uploadFile={uploadFile} 
                    file={file} 
                    isAuthenticated={isAuthenticated}
                  />
                ) : (
                  <FallbackComponent name="BotUpload" />
                )}
                
                {typeof Tournament === 'function' ? (
                  <Tournament 
                    runTournament={runTournament} 
                    isLoading={isLoading} 
                    tournamentLogs={tournamentLogs} 
                  />
                ) : (
                  <FallbackComponent name="Tournament" />
                )}
              </Box>
            </Container>
          ) : (
            typeof Auth === 'function' ? <Auth /> : <FallbackComponent name="Auth" />
          )}
        </div>
      )}
    </div>
  );
}

export default App;