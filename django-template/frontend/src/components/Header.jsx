import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Avatar,
  Menu,
  MenuItem,
  IconButton,
  Tooltip,
  useTheme
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { useHistory } from 'react-router-dom';


const Header = ({ userData }) => {
  const history = useHistory();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const theme = useTheme();

  const handleMenu = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);

  return (
    <AppBar
      position="static"
      elevation={3}
      sx={{
        background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
        mb: 4,
      }}
    >
      <Toolbar>
        <Typography
          variant="h5"
          sx={{
            flexGrow: 1,
            fontWeight: 700,
            letterSpacing: 1,
            color: '#fff',
            textShadow: '1px 1px 4px rgba(0,0,0,0.15)',
          }}
        >
          ♟️ Chess Bot Tournament
        </Typography>
        {userData && (
          <Box>
            <Tooltip title={userData.email}>
              <IconButton onClick={handleMenu} sx={{ p: 0 }}>
                <Avatar
                  sx={{
                    bgcolor: theme.palette.secondary.main,
                    width: 40,
                    height: 40,
                    fontWeight: 700,
                  }}
                  src={userData.avatar || undefined}
                >
                  {userData.name
                    ? userData.name[0].toUpperCase()
                    : userData.email
                    ? userData.email[0].toUpperCase()
                    : '?'}
                </Avatar>
              </IconButton>
            </Tooltip>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
              PaperProps={{
                sx: { minWidth: 180, mt: 1 },
              }}
            >
              <MenuItem
                onClick={() => {
                    handleClose();
                    history.push('/profile');
                }}
            >
                <AccountCircleIcon sx={{ mr: 1 }} /> Profile
              </MenuItem>
              <MenuItem
                component="a"
                href="http://localhost:8000/react-logout/"
                onClick={handleClose}
              >
                <LogoutIcon sx={{ mr: 1 }} /> Logout
              </MenuItem>
              {userData.role === 'teacher' && (
                <MenuItem
                  component="a"
                  href="http://localhost:8000/admin/"
                  onClick={handleClose}
                >
                  <AdminPanelSettingsIcon sx={{ mr: 1 }} /> Admin
                </MenuItem>
              )}
            </Menu>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header;