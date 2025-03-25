import React from 'react';
import { Button, Box, Typography, Paper } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';

const BotUpload = ({ handleFileChange, uploadFile, file, isAuthenticated }) => {
  return (
    <Paper elevation={3} sx={{ p: 3, mt: 2, mb: 4, width: '100%', maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>Upload Chess Bot</Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Button
            variant="contained"
            component="label"
            startIcon={<UploadFileIcon />}
          >
            Select File
            <input
              type="file"
              accept=".py"
              hidden
              onChange={handleFileChange}
            />
          </Button>
          <Typography variant="body1">
            {file ? file.name : "No file selected"}
          </Typography>
        </Box>
        
        <Button
          variant="contained"
          color="primary"
          onClick={uploadFile}
          disabled={!file}
        >
          Upload Bot
        </Button>
      </Box>
    </Paper>
  );
};

export default BotUpload;
