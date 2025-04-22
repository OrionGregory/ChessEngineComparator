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
      elevation={2}
      sx={{
        background: `linear-gradient(90deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 100%)`,
        mb: 4,
        boxShadow: '0 2px 6px rgba(0,0,0,0.08)',
      }}
    >
      <Toolbar sx={{ minHeight: 70 }}>
        <Typography
          variant="h6"
          sx={{
            flexGrow: 1,
            fontWeight: 600,
            color: '#f4f6f8',
            letterSpacing: 0.5,
          }}
        >
          Chess Bot Tournament
        </Typography>

        {userData && (
          <Box>
            <Tooltip title={userData.email}>
              <IconButton onClick={handleMenu} sx={{ p: 0 }}>
                <Avatar
                  sx={{
                    bgcolor: theme.palette.grey[200],
                    color: theme.palette.primary.main,
                    fontWeight: 600,
                    width: 36,
                    height: 36,
                    fontSize: 16,
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
                sx: {
                  mt: 1.5,
                  borderRadius: 2,
                  boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                },
              }}
            >
              <MenuItem
                onClick={() => {
                  handleClose();
                  history.push('/profile');
                }}
              >
                <AccountCircleIcon sx={{ mr: 1, fontSize: 20 }} /> Profile
              </MenuItem>
              <MenuItem
                component="a"
                href="http://localhost:8000/react-logout/"
                onClick={handleClose}
              >
                <LogoutIcon sx={{ mr: 1, fontSize: 20 }} /> Logout
              </MenuItem>
              {userData.role === 'teacher' && (
                <MenuItem
                  component="a"
                  href="http://localhost:8000/admin/"
                  onClick={handleClose}
                >
                  <AdminPanelSettingsIcon sx={{ mr: 1, fontSize: 20 }} /> Admin
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
