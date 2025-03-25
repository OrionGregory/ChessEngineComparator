import React from 'react';
import { Container, Box, Typography, Button, Paper } from '@mui/material';
import GoogleIcon from '@mui/icons-material/Google';

const Auth = () => {
  const handleGoogleLogin = () => {
    // Redirect to the backend OAuth endpoint
    window.location.href = "https://localhost:5000/auth/login";
  };
  
  return (
    <Container maxWidth="sm">
      <Box sx={{ 
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 'calc(100vh - 84px)' 
      }}>
        <Paper elevation={3} sx={{ p: 4, width: '100%', textAlign: 'center' }}>
          <Typography variant="h4" gutterBottom>
            Chess Bot Arena
          </Typography>
          
          <Typography variant="body1" sx={{ mb: 3 }}>
            Sign in with your Google account to access the Chess Bot Arena
          </Typography>
          
          <Button
            variant="contained"
            color="primary"
            size="large"
            startIcon={<GoogleIcon />}
            onClick={handleGoogleLogin}
            sx={{ py: 1.5 }}
          >
            Sign in with Google
          </Button>
        </Paper>
      </Box>
    </Container>
  );
};

export default Auth;
