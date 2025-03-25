import React, { useState } from 'react';
import { 
  Modal, 
  Box, 
  Typography, 
  TextField, 
  Button, 
  CircularProgress,
  Alert
} from '@mui/material';
import axios from 'axios';

const style = {
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

// Changed to const declaration to ensure proper export
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
      console.log('Sending update profile request to:', 'https://localhost:5000/api/update_profile');
      const response = await axios.post(
        'https://localhost:5000/api/update_profile',
        { username },
        { 
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json',
          }
        }
      );

      console.log('Profile update response:', response.data);
      if (response.data.success) {
        setSuccess(true);
        setTimeout(() => {
          handleClose();
          // Reload the page to reflect changes
          window.location.reload();
        }, 1500);
      }
    } catch (err) {
      console.error('Update profile error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      });
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
      <Box sx={style}>
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

// Make sure to export the component
export default ProfileEditModal;
