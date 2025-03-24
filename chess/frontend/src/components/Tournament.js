import React from 'react';
import { Box, Paper, Typography, Button, CircularProgress } from '@mui/material';

const Tournament = ({ runTournament, isLoading, tournamentLogs }) => {
  return (
    <Paper elevation={3} sx={{ mt: 4, width: '100%', maxWidth: 800, mx: 'auto', p: 2 }}>
      <Typography variant="h5" gutterBottom>
        Tournament Results
      </Typography>
      <Button variant="contained" color="primary" onClick={runTournament} disabled={isLoading} sx={{ mb: 2 }}>
        Run Tournament
      </Button>

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Paper
          sx={{
            backgroundColor: '#f5f5f5',
            p: 2,
            maxHeight: '400px',
            overflowY: 'auto',
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            fontSize: '0.9em'
          }}
        >
          {tournamentLogs || 'Click "Run Tournament" to see results'}
        </Paper>
      )}
    </Paper>
  );
};

export default Tournament;
