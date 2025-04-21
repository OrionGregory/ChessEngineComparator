import React from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  IconButton, 
  Box, 
  Drawer, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  Divider,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { styled } from '@mui/system';
import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import DashboardIcon from '@mui/icons-material/Dashboard';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import CodeIcon from '@mui/icons-material/Code';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import ChessIcon from '@mui/icons-material/Casino';
import { Link } from 'react-router-dom';
import axios from 'axios';

const Logo = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  marginRight: theme.spacing(2),
}));

const Navigation = ({ isAuthenticated, userData }) => {
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleLogout = async () => {
    try {
      // A simpler approach without CSRF token to get it working
      const response = await axios.post('/api/logout/', {}, {
        withCredentials: true
      });
      
      // Log the response for debugging
      console.log("Logout response:", response);
      
      // Always redirect to login page even if the API call fails
      localStorage.removeItem('userData');
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout request failed:', error);
      // Even if the API call fails, still "log out" locally
      localStorage.removeItem('userData');
      window.location.href = '/login';
    }
  };

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  const navItems = [
    { text: 'Home', icon: <HomeIcon />, path: '/' },
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Tournaments', icon: <EmojiEventsIcon />, path: '/tournaments' },
    { text: 'My Bots', icon: <CodeIcon />, path: '/bots' },
    { text: 'Profile', icon: <AccountCircleIcon />, path: '/profile' },
  ];

  const drawer = (
    <Box sx={{ width: 250 }} role="presentation">
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
        <ChessIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Chess Bot Tournament</Typography>
      </Box>
      <Divider />
      <List>
        {navItems.map((item) => (
          <ListItem 
            button
            component={Link} 
            key={item.text} 
            to={item.path}
            onClick={toggleDrawer}
            sx={{ cursor: 'pointer' }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem button onClick={handleLogout} sx={{ cursor: 'pointer' }}>
          <ListItemIcon><ExitToAppIcon /></ListItemIcon>
          <ListItemText primary="Logout" />
        </ListItem>
      </List>
    </Box>
  );

  return (
    <>
      <AppBar position="sticky">
        <Toolbar>
          {isAuthenticated && isMobile && (
            <IconButton
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={toggleDrawer}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}

          <Logo>
            <ChessIcon sx={{ mr: 1 }} />
            <Typography variant="h6" component="div">
              Chess Bot Tournament
            </Typography>
          </Logo>

          <Box sx={{ flexGrow: 1 }} />

          {isAuthenticated && !isMobile && (
            <Box sx={{ display: 'flex' }}>
              {navItems.map((item) => (
                <Button 
                  key={item.text}
                  color="inherit"
                  component={Link}
                  to={item.path}
                  startIcon={item.icon}
                  sx={{ mx: 0.5 }}
                >
                  {item.text}
                </Button>
              ))}
              <Button 
                color="inherit" 
                onClick={handleLogout}
                startIcon={<ExitToAppIcon />}
                sx={{ ml: 1 }}
              >
                Logout
              </Button>
            </Box>
          )}
          
          {!isAuthenticated && (
            <Button color="inherit" component={Link} to="/login">
              Login
            </Button>
          )}
        </Toolbar>
      </AppBar>

      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={toggleDrawer}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Navigation;