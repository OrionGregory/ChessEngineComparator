import React from 'react';
import { Box, Paper, Button, Input } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';

const BotUpload = ({ handleFileChange, uploadFile, file }) => {
  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
        <Input type="file" onChange={handleFileChange} accept=".py" sx={{ display: 'none' }} id="bot-upload" />
        <label htmlFor="bot-upload">
          <Button variant="contained" component="span" startIcon={<CloudUpload />}>
            Choose Bot File
          </Button>
        </label>
        <Button variant="contained" color="primary" onClick={uploadFile} disabled={!file}>
          Upload Bot
        </Button>
      </Box>
    </Paper>
  );
};

export default BotUpload;
