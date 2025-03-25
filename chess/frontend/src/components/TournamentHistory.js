import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Box, 
  Typography, 
  Paper, 
  List, 
  Button, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  Alert,
  AlertTitle,
  Badge,
  Chip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import RefreshIcon from '@mui/icons-material/Refresh';
import BugReportIcon from '@mui/icons-material/BugReport';

const TournamentHistory = () => {
  // State declarations
  const [tournaments, setTournaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTournament, setSelectedTournament] = useState(null);
  const [logContent, setLogContent] = useState('');
  const [open, setOpen] = useState(false);
  const [debugInfo, setDebugInfo] = useState('');
  const [showDebug, setShowDebug] = useState(true); // Default to true to help troubleshoot
  const [connectionStatus, setConnectionStatus] = useState('unknown');
  const [debugMessages, setDebugMessages] = useState([]);

  // Enhanced debug function with timestamp and visual indicator
  const addDebugInfo = (message) => {
    const timestamp = new Date().toISOString();
    console.log(`[TournamentHistory ${timestamp}] ${message}`);
    setDebugInfo(prev => `${prev}\n[${timestamp}] ${message}`);
    
    // Add visual debug message that appears at top of component
    setDebugMessages(prev => [...prev.slice(-4), { 
      id: Date.now(), 
      message, 
      timestamp 
    }]);
  };

  // Check API connection on mount
  useEffect(() => {
    addDebugInfo('Component mounted - Checking API connection...');
    checkConnection();
    
    // Add force refresh on tab visibility change (helps with browser caching)
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        addDebugInfo('Tab became visible - Refreshing data');
        refreshData();
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  // Test API connection
  const checkConnection = async () => {
    try {
      addDebugInfo('Testing API connection...');
      // Add cache busting parameter to avoid cached responses
      const response = await axios.get('https://localhost:5000/tournament_history', {
        withCredentials: true,
        params: { _: Date.now() } // Cache busting
      });
      setConnectionStatus('connected');
      addDebugInfo(`API connection successful: ${response.status}`);
    } catch (err) {
      setConnectionStatus('failed');
      addDebugInfo(`API connection failed: ${err.message}`);
    }
  };

  // Combined refresh function
  const refreshData = () => {
    checkConnection();
    fetchTournaments(true);
  };

  const fetchTournaments = async (forceRefresh = false) => {
    addDebugInfo(`Fetching tournament history (force=${forceRefresh})...`);
    try {
      setLoading(true);
      
      // Add cache busting to prevent cached responses
      const response = await axios.get('https://localhost:5000/tournament_history', {
        withCredentials: true,
        params: { _: Date.now() },
        headers: forceRefresh ? {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
          'Expires': '0'
        } : {}
      });
      
      addDebugInfo(`Received response: status=${response.status}`);
      
      // Debug data structure
      const dataKeys = Object.keys(response.data || {});
      addDebugInfo(`Response data keys: ${dataKeys.join(', ')}`);
      
      if (response.data && Array.isArray(response.data.tournaments)) {
        const tournamentCount = response.data.tournaments.length;
        addDebugInfo(`Received ${tournamentCount} tournaments`);
        setTournaments(response.data.tournaments);
        
        // Show sample data for debugging
        if (tournamentCount > 0) {
          const sample = response.data.tournaments[0];
          addDebugInfo(`Sample tournament: ID=${sample.id}, Winner=${sample.winner || 'none'}`);
        }
        
        setError(null);
      } else {
        addDebugInfo('Response has unexpected format, missing tournaments array');
        // Show the actual response for debugging
        addDebugInfo(`Actual response: ${JSON.stringify(response.data)}`);
        setError('Server returned an unexpected response format. Check debug panel.');
      }
    } catch (err) {
      // Enhanced error logging
      const errorMsg = err.response ? 
        `Server error: ${err.response.status} - ${err.response.data?.error || err.message}` : 
        `Network error: ${err.message}`;
      
      addDebugInfo(`Error fetching tournaments: ${errorMsg}`);
      
      // Show more detailed error information
      if (err.response) {
        addDebugInfo(`Response error data: ${JSON.stringify(err.response.data || {})}`);
      }
      
      console.error('Error fetching tournament history:', err);
      setError(`Failed to load tournament history: ${errorMsg}`);
    } finally {
      setLoading(false);
      addDebugInfo('Fetch operation completed');
    }
  };

  const handleViewLog = async (tournamentId) => {
    addDebugInfo(`Viewing log for tournament: ${tournamentId}`);
    try {
      setLoading(true);
      addDebugInfo(`Fetching log content from /tournament_log/${tournamentId}`);
      
      const response = await axios.get(`https://localhost:5000/tournament_log/${tournamentId}`, {
        withCredentials: true,
        params: { _: Date.now() } // Cache busting
      });
      
      // Log response success
      addDebugInfo(`Received log response: status=${response.status}`);
      
      if (response.data && response.data.tournament && response.data.log_content) {
        setSelectedTournament(response.data.tournament);
        setLogContent(response.data.log_content);
        const contentLength = response.data.log_content.length;
        addDebugInfo(`Log content loaded successfully, ${contentLength} characters`);
        setOpen(true);
      } else {
        addDebugInfo('Response has unexpected format, missing tournament or log_content');
        // Show what was actually received
        const keys = Object.keys(response.data || {});
        addDebugInfo(`Received keys: ${keys.join(', ')}`);
        setError('Server returned an incomplete response for the tournament log');
      }
    } catch (err) {
      const errorMsg = err.response ? 
        `Server error: ${err.response.status} - ${err.response.data?.error || err.message}` : 
        `Network error: ${err.message}`;
      
      addDebugInfo(`Error fetching tournament log: ${errorMsg}`);
      console.error('Error fetching tournament log:', err);
      
      setError(`Failed to load tournament log: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setOpen(false);
    addDebugInfo('Closed log dialog');
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch (e) {
      addDebugInfo(`Error formatting date "${dateString}": ${e.message}`);
      return 'Invalid date';
    }
  };

  const showDebugPanel = () => {
    return (
      <Accordion sx={{ mt: 2, mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography color="text.secondary">Debug Information</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box component="pre" sx={{ 
            whiteSpace: 'pre-wrap', 
            wordBreak: 'break-word',
            fontSize: '0.75rem',
            fontFamily: 'monospace',
            p: 1,
            backgroundColor: '#f5f5f5',
            borderRadius: 1,
            maxHeight: '300px',
            overflow: 'auto'
          }}>
            Tournament Count: {tournaments.length}
            Loading State: {loading ? 'true' : 'false'}
            Error State: {error ? error : 'none'}
            Selected Tournament: {selectedTournament ? selectedTournament.id : 'none'}
            Dialog Open: {open ? 'true' : 'false'}
            Log Content Length: {logContent.length} characters
            
            --- Debug Timeline ---
            {debugInfo}
          </Box>
          <Button 
            variant="outlined" 
            size="small" 
            onClick={fetchTournaments} 
            sx={{ mt: 1 }}
          >
            Refresh Data
          </Button>
        </AccordionDetails>
      </Accordion>
    );
  };

  // Render debug toolbar for quick actions
  const renderDebugToolbar = () => (
    <Box sx={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      mb: 2,
      p: 1,
      backgroundColor: '#f5f5f5',
      borderRadius: 1
    }}>
      <Box>
        <Chip 
          icon={<BugReportIcon />}
          label="Debug Mode" 
          color="secondary"
          variant="outlined"
          sx={{ mr: 1 }}
        />
        <Chip 
          label={`API: ${connectionStatus}`} 
          color={connectionStatus === 'connected' ? 'success' : connectionStatus === 'failed' ? 'error' : 'default'}
          variant="outlined"
        />
      </Box>
      <Box>
        <Button 
          startIcon={<RefreshIcon />}
          variant="outlined" 
          size="small" 
          onClick={() => refreshData(true)}
        >
          Force Refresh
        </Button>
      </Box>
    </Box>
  );

  // Render latest debug messages
  const renderDebugMessages = () => (
    <Box sx={{ mb: 2 }}>
      {debugMessages.map(msg => (
        <Alert 
          key={msg.id}
          severity="info" 
          sx={{ mb: 1 }}
          icon={<BugReportIcon fontSize="inherit" />}
        >
          <Typography variant="caption" component="span" sx={{ fontFamily: 'monospace' }}>
            {new Date(msg.timestamp).toLocaleTimeString()}:
          </Typography>{' '}
          {msg.message}
        </Alert>
      ))}
    </Box>
  );

  // Main rendering logic
  if (loading && tournaments.length === 0) {
    return (
      <Box display="flex" flexDirection="column" alignItems="center" p={3}>
        {renderDebugToolbar()}
        {renderDebugMessages()}
        <CircularProgress />
        <Typography variant="body2" sx={{ mt: 2 }}>
          Loading tournament history...
        </Typography>
        {showDebugPanel()}
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 4, mb: 4, width: '100%' }}>
      {showDebug && renderDebugToolbar()}
      {showDebug && renderDebugMessages()}
      
      <Typography variant="h5" gutterBottom>
        Your Tournament History
        <Badge 
          badgeContent={tournaments.length} 
          color="primary"
          sx={{ ml: 2 }}
        />
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          <AlertTitle>Error</AlertTitle>
          {error}
          <Button 
            variant="outlined" 
            size="small" 
            onClick={() => refreshData(true)} 
            sx={{ mt: 1 }}
          >
            Force Retry
          </Button>
        </Alert>
      )}
      
      {tournaments.length === 0 ? (
        <Paper elevation={2} sx={{ p: 3, mt: 2 }}>
          <Typography>You haven't run any tournaments yet.</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Run a tournament to see your history here.
          </Typography>
        </Paper>
      ) : (
        <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
          {tournaments.map((tournament) => (
            <Paper 
              key={tournament.id} 
              elevation={2} 
              sx={{ 
                mb: 2, 
                borderRadius: 2, 
                overflow: 'hidden',
                '&:hover': {
                  boxShadow: 3,
                },
              }}
            >
              <Accordion>
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  aria-controls={`tournament-${tournament.id}-content`}
                  id={`tournament-${tournament.id}-header`}
                >
                  <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      Tournament {tournament.id.substring(0, 8)}...
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {formatDate(tournament.start_time)}
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ p: 0 }}>
                  <Divider />
                  <Box sx={{ p: 2 }}>
                    <Typography variant="body2">
                      <strong>Winner:</strong> {tournament.winner || 'No winner'}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Participants:</strong> {Array.isArray(tournament.participants) ? 
                        tournament.participants.join(', ') : 
                        'No participants recorded'}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Start Time:</strong> {formatDate(tournament.start_time)}
                    </Typography>
                    <Typography variant="body2">
                      <strong>End Time:</strong> {formatDate(tournament.end_time)}
                    </Typography>
                    <Button 
                      variant="contained" 
                      size="small" 
                      onClick={() => handleViewLog(tournament.id)}
                      sx={{ mt: 2 }}
                    >
                      View Full Log
                    </Button>
                  </Box>
                </AccordionDetails>
              </Accordion>
            </Paper>
          ))}
        </List>
      )}

      {showDebug && showDebugPanel()}

      <Dialog 
        open={open} 
        onClose={handleClose} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          Tournament Log
          {selectedTournament && (
            <Typography variant="subtitle2" color="text.secondary">
              ID: {selectedTournament.id}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent dividers>
          {loading ? (
            <Box display="flex" justifyContent="center" p={3}>
              <CircularProgress />
            </Box>
          ) : logContent ? (
            <Box 
              component="pre" 
              sx={{ 
                whiteSpace: 'pre-wrap', 
                wordBreak: 'break-word',
                fontSize: '0.875rem',
                fontFamily: 'monospace',
                p: 1,
                maxHeight: '60vh',
                overflow: 'auto'
              }}
            >
              {logContent}
            </Box>
          ) : (
            <Box p={2}>
              <Alert severity="warning">
                <AlertTitle>No Content</AlertTitle>
                The log file is empty or could not be loaded.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TournamentHistory;
