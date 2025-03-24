import React from 'react';
import { Box, Paper, Button, Input, Typography } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';

const BotUpload = ({ handleFileChange, uploadFile, file, isAuthenticated }) => {
  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
        <Input type="file" onChange={handleFileChange} accept=".py" sx={{ display: 'none' }} id="bot-upload" />
        <label htmlFor="bot-upload">
          <Button variant="contained" component="span" startIcon={<CloudUpload />} disabled={!isAuthenticated}>
            Choose Bot File
          </Button>
        </label>
        <Button
          variant="contained"
          color="primary"
          onClick={uploadFile}
          disabled={!file || !isAuthenticated}
        >
          Upload Bot
        </Button>
      </Box>
      {!isAuthenticated && (
        <Typography color="error" variant="body2" sx={{ mt: 2 }}>
          You must be logged in to upload a bot.
        </Typography>
      )}
    </Paper>
  );
};

export default BotUpload;
