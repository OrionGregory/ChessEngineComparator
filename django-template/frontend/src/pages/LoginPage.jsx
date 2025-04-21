import React from 'react';
import { 
  Box, 
  Button, 
  Container, 
  Typography, 
  Paper, 
  Divider,
  useTheme,
  useMediaQuery,
  IconButton
} from '@mui/material';
import GoogleIcon from '@mui/icons-material/Google';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import ChessIcon from '@mui/icons-material/Casino';
import { styled } from '@mui/system';

const LoginPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  borderRadius: 16,
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
  transition: 'transform 0.3s ease-in-out',
  '&:hover': {
    transform: 'translateY(-5px)',
  },
}));

const GoogleButton = styled(Button)(({ theme }) => ({
  color: theme.palette.getContrastText(theme.palette.common.white),
  backgroundColor: theme.palette.common.white,
  borderRadius: 8,
  padding: theme.spacing(1.5, 3),
  boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
  marginTop: theme.spacing(2),
  textTransform: 'none',
  fontWeight: 'bold',
  '&:hover': {
    backgroundColor: '#f8f8f8',
  }
}));

const ChessLogo = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: theme.spacing(3),
}));

const ThemeToggle = styled(IconButton)(({ theme }) => ({
  position: 'absolute',
  top: theme.spacing(2),
  right: theme.spacing(2),
}));

const ChessBoardBackground = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  opacity: 0.03,
  zIndex: -1,
  backgroundImage: `
    linear-gradient(45deg, ${theme.palette.background.default} 25%, transparent 25%),
    linear-gradient(-45deg, ${theme.palette.background.default} 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, ${theme.palette.background.default} 75%),
    linear-gradient(-45deg, transparent 75%, ${theme.palette.background.default} 75%)
  `,
  backgroundSize: '40px 40px',
  backgroundPosition: '0 0, 0 20px, 20px -20px, -20px 0px',
}));

const LoginPage = ({ toggleTheme, mode, authError }) => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
    const handleGoogleLogin = () => {
        const currentOrigin = window.location.origin;
        
        // Use the direct Google login endpoint
        window.location.href = 'http://localhost:8000/auth/direct-google-login/?next=' + encodeURIComponent(currentOrigin);
      };
  
  return (
    <Container component="main" maxWidth="xs" sx={{ 
      height: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      position: 'relative'
    }}>
      <ChessBoardBackground />
      
      <ThemeToggle onClick={toggleTheme} color="inherit" aria-label="toggle theme">
        {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
      </ThemeToggle>
      
      <LoginPaper elevation={3}>
        <ChessLogo>
          <ChessIcon sx={{ 
            fontSize: isMobile ? 40 : 48,
            color: theme.palette.primary.main 
          }} />
        </ChessLogo>
        
        <Typography variant="h4" component="h1" gutterBottom sx={{ 
          fontWeight: 'bold',
          textAlign: 'center',
          fontSize: isMobile ? '1.75rem' : '2.125rem'
        }}>
          Chess Bot Tournament
        </Typography>
        
        <Typography variant="body1" sx={{ 
          mb: 3, 
          textAlign: 'center',
          color: theme.palette.text.secondary,
          fontSize: isMobile ? '0.875rem' : '1rem'
        }}>
          Sign in to manage and compete with your chess bots
        </Typography>
        
        <Divider sx={{ width: '100%', mb: 3 }} />
        
        <GoogleButton
          startIcon={<GoogleIcon />}
          variant="contained"
          fullWidth
          onClick={handleGoogleLogin}
          size={isMobile ? "medium" : "large"}
        >
          Sign in with Google
        </GoogleButton>
        
        <Typography variant="caption" sx={{ 
          mt: 3, 
          textAlign: 'center', 
          color: theme.palette.text.secondary,
          fontSize: isMobile ? '0.65rem' : '0.75rem'
        }}>
          By signing in, you agree to our Terms of Service and Privacy Policy
        </Typography>
      </LoginPaper>
    </Container>
  );
};

export default LoginPage;