import React, { useState } from 'react';
import { Container, Box, Typography, TextField, Button, Paper, Link } from '@mui/material';
import LoginIcon from '@mui/icons-material/Login';
import PersonAddIcon from '@mui/icons-material/PersonAdd';

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  
  const toggleMode = () => {
    setIsLogin(!isLogin);
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
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography variant="h4" align="center" gutterBottom>
            {isLogin ? 'Login' : 'Register'}
          </Typography>
          
          <Box component="form" noValidate sx={{ mt: 2 }}>
            {!isLogin && (
              <TextField
                margin="normal"
                required
                fullWidth
                id="name"
                label="Full Name"
                name="name"
                autoComplete="name"
                autoFocus={!isLogin}
              />
            )}
            
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus={isLogin}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete={isLogin ? "current-password" : "new-password"}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              startIcon={isLogin ? <LoginIcon /> : <PersonAddIcon />}
            >
              {isLogin ? 'Sign In' : 'Sign Up'}
            </Button>
            
            <Box sx={{ textAlign: 'center' }}>
              <Link
                component="button"
                variant="body2"
                onClick={toggleMode}
              >
                {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Sign In"}
              </Link>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Auth;
