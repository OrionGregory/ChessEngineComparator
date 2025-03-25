import React, { useState } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Box,
  Modal,
  TextField,
  CircularProgress,
  Alert
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import LoginIcon from '@mui/icons-material/Login';
import EditIcon from '@mui/icons-material/Edit';
import axios from 'axios';

// Define the modal style here in the same file
const modalStyle = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: 'background.paper',
  boxShadow: 24,
  p: 4,
  borderRadius: 2,
};

// Inline ProfileEditModal component
const ProfileEditModal = ({ open, handleClose, userData }) => {
  const [username, setUsername] = useState(userData?.username || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const response = await axios.post(
        'https://localhost:5000/update_profile',
        { username },
        { withCredentials: true }
      );

      if (response.data.success) {
        setSuccess(true);
        setTimeout(() => {
          handleClose();
          // Reload the page to reflect changes
          window.location.reload();
        }, 1500);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      aria-labelledby="profile-edit-modal"
    >
      <Box sx={modalStyle}>
        <Typography id="profile-edit-modal" variant="h6" component="h2" mb={3}>
          Edit Profile
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Profile updated successfully!
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            margin="normal"
            required
            inputProps={{ minLength: 3, maxLength: 30 }}
          />

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            <Button 
              variant="outlined" 
              onClick={handleClose}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              variant="contained"
              disabled={loading || !username || username === userData?.username}
            >
              {loading ? <CircularProgress size={24} /> : 'Save Changes'}
            </Button>
          </Box>
        </form>
      </Box>
    </Modal>
  );
};

function NavbarComponent({ isAuthenticated, userData, handleLogout }) {
  const [openProfileEdit, setOpenProfileEdit] = useState(false);

  const handleOpenProfileEdit = () => {
    setOpenProfileEdit(true);
  };

  const handleCloseProfileEdit = () => {
    setOpenProfileEdit(false);
  };

  // Full-width styling with no borders
  return (
    <AppBar 
      position="fixed"
      sx={{
        top: 0,
        left: 0,
        right: 0,
        width: '100vw',
        margin: 0,
        padding: 0,
        border: 'none',
        borderRadius: 0,
        boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
        zIndex: 1300
      }}
    >
      <Toolbar sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        width: '100%',
        padding: {xs: '0 16px', sm: '0 24px'},
        minHeight: '64px'
      }}>
        <Typography variant="h6" component="div">
          Chess Bot Arena
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {isAuthenticated ? (
            <>
              {userData && (
                <Typography variant="body1" sx={{ mr: 2 }}>
                  {userData.username || 'User'}
                </Typography>
              )}
              <Button 
                variant="outlined"
                color="inherit" 
                onClick={handleOpenProfileEdit}
                startIcon={<EditIcon />}
                sx={{ mr: 2 }}
              >
                Edit Profile
              </Button>
              <Button 
                variant="contained"
                color="secondary" 
                onClick={handleLogout}
                startIcon={<LogoutIcon />}
              >
                Logout
              </Button>
            </>
          ) : (
            <Button 
              variant="contained"
              color="secondary" 
              href="/login"
              startIcon={<LoginIcon />}
            >
              Login
            </Button>
          )}
        </Box>
      </Toolbar>

      {/* Profile Edit Modal - now using the inline component */}
      {isAuthenticated && userData && (
        <ProfileEditModal 
          open={openProfileEdit} 
          handleClose={handleCloseProfileEdit} 
          userData={userData}
        />
      )}
    </AppBar>
  );
}

export default NavbarComponent;
