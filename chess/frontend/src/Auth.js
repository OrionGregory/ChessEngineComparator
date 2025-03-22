import React, { useEffect, useState } from "react";
import { 
  Button, 
  Container, 
  TextField, 
  Typography, 
  Box, 
  Alert, 
  CircularProgress,
  Paper,
  Avatar 
} from "@mui/material";
import GoogleIcon from '@mui/icons-material/Google';
import LogoutIcon from '@mui/icons-material/Logout';
import PersonIcon from '@mui/icons-material/Person';
import axios from "axios";

const Auth = () => {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [googleId, setGoogleId] = useState("");
  const [isSigningUp, setIsSigningUp] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [welcomeMessage, setWelcomeMessage] = useState("");
  const [error, setError] = useState("");
  const [userData, setUserData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  axios.defaults.withCredentials = true;

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const emailParam = params.get("email");
    const nameParam = params.get("name");
    const googleIdParam = params.get("google_id");

    if (emailParam && nameParam && googleIdParam) {
      setEmail(emailParam);
      setName(nameParam);
      setGoogleId(googleIdParam);
      setIsSigningUp(true);
    }
    setIsLoading(false);
  }, []);

  
  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        // Avoid checking login status if the user is being redirected for OAuth
        if (window.location.pathname === "/auth/callback") {
          return;
        }
  
        const response = await axios.get("https://localhost:5000/home", {
          withCredentials: true,
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
        });
  
        if (response.status === 200) {
          setIsLoggedIn(true);
          setUserData(response.data.user);
          setWelcomeMessage(response.data.message);
        }
      } catch (err) {
        if (err.response?.status === 401) {
          // Not logged in - redirect to login page if not already there
          if (window.location.pathname !== "/") {
            window.location.replace("https://localhost:3000/");
          }
        }
      } finally {
        setIsLoading(false);
      }
    };
  
    // Only check login status if we're not in the signup process
    if (!isSigningUp) {
      checkLoginStatus();
    } else {
      setIsLoading(false);
    }
  }, [isSigningUp]);

  const handleGoogleAuth = () => {
    window.location.href = "https://localhost:5000/auth/login";
};

 const handleSignup = async () => {
    if (!username.trim()) {
      setError("Username is required");
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post("https://localhost:5000/auth/signup", {
        google_id: googleId,
        email,
        name,
        username,
      });

      if (response.status === 200) {
        setIsLoggedIn(true);
        // Use the redirect URL from the response
        window.location.replace(`https://localhost:3000${response.data.redirect_url}`);
      }
    } catch (err) {
      setError(err.response?.data?.error || "Signup failed");
    } finally {
      setIsLoading(false);
    }
};

  const handleLogout = async () => {
    try {
      const response = await axios.get("https://localhost:5000/auth/logout", {
        withCredentials: true
      });
      
      if (response.status === 200) {
        setIsLoggedIn(false);
        setUserData(null);
        setWelcomeMessage("");
        window.location.replace("https://localhost:3000/");
      }
    } catch (err) {
      setError("Logout failed: " + (err.response?.data?.error || "Unknown error"));
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="sm">
        <Box 
          display="flex" 
          justifyContent="center" 
          alignItems="center" 
          minHeight="80vh"
        >
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (isLoggedIn && userData) {
    return (
      <Container maxWidth="sm">
        <Paper 
          elevation={3}
          sx={{
            mt: 8,
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            borderRadius: 2
          }}
        >
          <Avatar sx={{ 
            width: 60, 
            height: 60, 
            bgcolor: 'primary.main',
            mb: 2 
          }}>
            <PersonIcon fontSize="large" />
          </Avatar>

          <Typography variant="h4" component="h1" gutterBottom color="primary">
            {welcomeMessage}
          </Typography>

          <Box 
            sx={{
              mt: 3,
              width: '100%',
              bgcolor: 'background.paper',
              borderRadius: 1,
              p: 2
            }}
          >
            <Typography variant="h6" gutterBottom color="textSecondary">
              Profile Information
            </Typography>
            <Typography variant="body1" gutterBottom>
              <strong>Username:</strong> {userData.username}
            </Typography>
            <Typography variant="body1" gutterBottom>
              <strong>Email:</strong> {userData.email}
            </Typography>
          </Box>

          <Button 
            variant="contained" 
            color="secondary" 
            onClick={handleLogout}
            startIcon={<LogoutIcon />}
            sx={{ mt: 4 }}
            size="large"
          >
            Logout
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm">
      <Paper 
        elevation={3}
        sx={{
          mt: 8,
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          borderRadius: 2
        }}
      >
        <Typography variant="h4" gutterBottom color="primary">
          {isSigningUp ? "Complete Your Profile" : "Welcome"}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
            {error}
          </Alert>
        )}

        {isSigningUp ? (
          <>
            <TextField
              fullWidth
              label="Username"
              variant="outlined"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              margin="normal"
              sx={{ mb: 2 }}
            />
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleSignup}
              fullWidth
              size="large"
              disabled={isLoading}
            >
              {isLoading ? <CircularProgress size={24} /> : "Complete Signup"}
            </Button>
          </>
        ) : (
          <Button
            variant="contained"
            color="primary"
            onClick={handleGoogleAuth}
            startIcon={<GoogleIcon />}
            size="large"
            sx={{ mt: 2 }}
          >
            Sign in with Google
          </Button>
        )}
      </Paper>
    </Container>
  );
};

export default Auth;