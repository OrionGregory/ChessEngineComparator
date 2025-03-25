import React from 'react';
import { Button, Box, Typography, Paper, CircularProgress, TextField } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const Tournament = ({ runTournament, isLoading, tournamentLogs }) => {
  return (
    <Paper elevation={3} sx={{ p: 3, mt: 2, width: '100%', maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>Tournament</Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<PlayArrowIcon />}
          onClick={runTournament}
          disabled={isLoading}
        >
          {isLoading ? 'Running...' : 'Run Tournament'}
        </Button>
        
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress />
          </Box>
        )}
        
        {tournamentLogs && (
          <TextField
            label="Tournament Logs"
            multiline
            rows={10}
            variant="outlined"
            fullWidth
            value={tournamentLogs}
            InputProps={{
              readOnly: true,
            }}
            sx={{ mt: 2, fontFamily: 'monospace' }}
          />
        )}
      </Box>
    </Paper>
  );
};

export default Tournament;
