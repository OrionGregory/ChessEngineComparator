import React, { useEffect, useState } from "react";
import { Button, Container, Typography, Box, CircularProgress, Paper } from "@mui/material";
import GoogleIcon from '@mui/icons-material/Google';
import LogoutIcon from '@mui/icons-material/Logout';
import axios from "axios";

const Auth = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const checkLoginStatus = async () => {
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

    checkLoginStatus();
  }, []);

  const handleGoogleAuth = () => {
    window.location.href = "https://localhost:5000/auth/login";
  };

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

  if (isLoading) {
    return (
      <Container maxWidth="sm">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return isAuthenticated ? (
    <Container maxWidth="sm">
      <Paper elevation={3} sx={{ mt: 8, p: 4, textAlign: 'center', borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom>Welcome, {userData?.name}!</Typography>
        <Typography variant="body1">Username: {userData?.username}</Typography>
        <Typography variant="body1">Email: {userData?.email}</Typography>
        <Button variant="contained" color="secondary" onClick={handleLogout} startIcon={<LogoutIcon />} sx={{ mt: 3 }}>
          Logout
        </Button>
      </Paper>
    </Container>
  ) : (
    <Container maxWidth="sm">
      <Box display="flex" flexDirection="column" alignItems="center" minHeight="100vh" justifyContent="center">
        <Typography variant="h4" gutterBottom>Sign in to continue</Typography>
        <Button variant="contained" color="primary" onClick={handleGoogleAuth} startIcon={<GoogleIcon />} size="large">
          Sign in with Google
        </Button>
      </Box>
    </Container>
  );
};

export default Auth;
