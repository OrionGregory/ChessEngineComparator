import React from 'react';
import { Box, Container, Paper, Toolbar, useTheme, useMediaQuery, IconButton } from '@mui/material';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/system';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import Navigation from './Navigation';


const PageWrapper = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.default,
}));

const ContentWrapper = styled(Container)(({ theme }) => ({
  flexGrow: 1,
  paddingTop: theme.spacing(3),
  paddingBottom: theme.spacing(3),
}));

const MainLayout = ({ 
  children, 
  title, 
  maxWidth = 'lg', 
  isAuthenticated, 
  userData, 
  toggleTheme, 
  mode 
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <PageWrapper>
      <Navigation isAuthenticated={isAuthenticated} userData={userData} />
      
      <ContentWrapper maxWidth={maxWidth}>
        {title && (
          <Box 
            sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              mb: 3
            }}
          >
            <Typography 
              variant={isMobile ? 'h5' : 'h4'} 
              component="h1"
            >
              {title}
            </Typography>
            
            <IconButton 
              onClick={toggleTheme} 
              color="inherit" 
              aria-label="toggle theme"
            >
              {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Box>
        )}
        
        {children}
      </ContentWrapper>
      
      <Box 
        component="footer" 
        sx={{ 
          py: 2, 
          textAlign: 'center',
          bgcolor: theme.palette.background.paper,
          borderTop: `1px solid ${theme.palette.divider}`,
          mt: 'auto'
        }}
      >
        <Typography variant="body2" color="text.secondary">
          © {new Date().getFullYear()} Chess Bot Tournament. All rights reserved.
        </Typography>
      </Box>
    </PageWrapper>
  );
};

export default MainLayout;