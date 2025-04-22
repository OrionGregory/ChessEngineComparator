import React, { useState, useEffect } from 'react';
import {
  Box, Paper, Typography, Button, CircularProgress, Chip,
  Grid, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, InputAdornment, Alert, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, LinearProgress
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Search as SearchIcon,
  Add as AddIcon,
  PlayArrow as PlayArrowIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { useParams, useHistory } from 'react-router-dom';
import apiService from '../services/apiService';

const TournamentDetailsPage = ({ userData }) => {
  const { id } = useParams();
  const history = useHistory();

  // State for tournament data
  const [loading, setLoading] = useState(true);
  const [tournament, setTournament] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [matches, setMatches] = useState([]);
  const [error, setError] = useState(null);

  // State for add participant modal
  const [openAddBotModal, setOpenAddBotModal] = useState(false);
  const [availableBots, setAvailableBots] = useState([]);
  const [selectedBots, setSelectedBots] = useState([]);
  const [botSearch, setBotSearch] = useState('');
  const [addingBots, setAddingBots] = useState(false);
  const [botError, setBotError] = useState('');
  const [botSuccess, setBotSuccess] = useState('');

  // State for delete tournament modal
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState('');
  const [deleteSuccess, setDeleteSuccess] = useState('');

  // Load tournament data
  useEffect(() => {
    const fetchTournamentData = async () => {
      setLoading(true);
      try {
        const response = await apiService.getTournament(id);
        setTournament(response.data);
        setParticipants(response.data.participants || []);
        setMatches(response.data.matches || []);
      } catch (err) {
        console.error('Error loading tournament:', err);
        setError('Failed to load tournament details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchTournamentData();
  }, [id]);

  // Load available bots when add bot modal opens
  const handleOpenAddBotModal = async () => {
    setBotError('');
    setBotSuccess('');
    setSelectedBots([]);
    setBotSearch('');
    setAddingBots(false);
    
    try {
      // Get all active bots
      const response = await apiService.getBots();
      const activeBots = response.data.filter(bot => bot.status === 'active');
      
      // Filter out bots already in the tournament
      const currentBotIds = participants.map(p => p.bot_id);
      const availableBotsList = activeBots.filter(bot => !currentBotIds.includes(bot.id));
      
      setAvailableBots(availableBotsList);
      setOpenAddBotModal(true);
    } catch (err) {
      console.error('Error loading bots:', err);
      setBotError('Failed to load available bots. Please try again later.');
    }
  };

  // Filter available bots based on search term
  const filteredBots = availableBots.filter(
    bot => 
      bot.name.toLowerCase().includes(botSearch.toLowerCase()) ||
      (bot.owner_email && bot.owner_email.toLowerCase().includes(botSearch.toLowerCase())) ||
      (bot.description && bot.description.toLowerCase().includes(botSearch.toLowerCase()))
  );

  // Toggle bot selection
  const toggleBotSelection = (botId) => {
    if (selectedBots.includes(botId)) {
      setSelectedBots(selectedBots.filter(id => id !== botId));
    } else {
      setSelectedBots([...selectedBots, botId]);
    }
  };

  // Toggle select all bots
  const toggleSelectAll = () => {
    if (selectedBots.length === filteredBots.length) {
      setSelectedBots([]);
    } else {
      setSelectedBots(filteredBots.map(bot => bot.id));
    }
  };

  // Add selected bots to tournament
  const addSelectedBots = async () => {
    if (selectedBots.length === 0) {
      setBotError('Please select at least one bot to add.');
      return;
    }

    setAddingBots(true);
    setBotError('');
    setBotSuccess('Adding bots to tournament...');
    
    let successCount = 0;
    let failCount = 0;
    
    // Add bots sequentially
    for (const botId of selectedBots) {
      try {
        await apiService.addParticipant(id, botId);
        successCount++;
      } catch (err) {
        console.error(`Error adding bot ${botId}:`, err);
        failCount++;
      }
    }
    
    if (successCount > 0) {
      // Refresh tournament data to show new participants
      const response = await apiService.getTournament(id);
      setTournament(response.data);
      setParticipants(response.data.participants || []);
      
      // Update available bots list
      const updatedAvailableBots = availableBots.filter(bot => !selectedBots.includes(bot.id));
      setAvailableBots(updatedAvailableBots);
      setSelectedBots([]);
      
      setBotSuccess(`Successfully added ${successCount} bot(s)${failCount > 0 ? `. Failed to add ${failCount} bot(s).` : ''}`);
    } else {
      setBotError('Failed to add any bots to the tournament.');
    }
    
    setAddingBots(false);
  };

  // Remove participant from tournament
  const removeParticipant = async (botId) => {
    if (!window.confirm('Are you sure you want to remove this bot from the tournament?')) {
      return;
    }
    
    try {
      await apiService.removeParticipant(id, botId);
      
      // Refresh tournament data
      const response = await apiService.getTournament(id);
      setTournament(response.data);
      setParticipants(response.data.participants || []);
    } catch (err) {
      console.error('Error removing participant:', err);
      alert('Failed to remove participant. Please try again.');
    }
  };

  // Start tournament
  const startTournament = async () => {
    if (!window.confirm('Are you sure you want to start this tournament? This will generate all matches and cannot be undone.')) {
      return;
    }
    
    try {
      await apiService.startTournament(id);
      
      // Refresh tournament data
      const response = await apiService.getTournament(id);
      setTournament(response.data);
      setParticipants(response.data.participants || []);
      setMatches(response.data.matches || []);
      
      alert('Tournament started successfully!');
    } catch (err) {
      console.error('Error starting tournament:', err);
      alert(err.response?.data?.error || 'Failed to start tournament. Please try again.');
    }
  };

  // Recalculate tournament scores
  const recalculateScores = async () => {
    if (!window.confirm('Are you sure you want to recalculate all tournament scores?')) {
      return;
    }
    
    try {
      await apiService.recalculateScores(id);
      
      // Refresh tournament data
      const response = await apiService.getTournament(id);
      setTournament(response.data);
      setParticipants(response.data.participants || []);
      setMatches(response.data.matches || []);
      
      alert('Scores recalculated successfully!');
    } catch (err) {
      console.error('Error recalculating scores:', err);
      alert('Failed to recalculate scores. Please try again.');
    }
  };

  // Delete tournament
  const deleteTournament = async () => {
    setDeleting(true);
    setDeleteError('');
    setDeleteSuccess('');
    
    try {
      await apiService.deleteTournament(id);
      setDeleteSuccess('Tournament deleted successfully! Redirecting...');
      
      // Redirect after a delay
      setTimeout(() => {
        history.push('/profile');
      }, 1500);
    } catch (err) {
      console.error('Error deleting tournament:', err);
      setDeleteError(err.response?.data?.error || err.response?.data?.detail || 'Failed to delete tournament. Please try again.');
      setDeleting(false);
    }
  };

  // Cancel tournament
  const cancelTournament = async () => {
    if (!window.confirm('Are you sure you want to cancel this tournament?')) {
      return;
    }
    
    try {
      await apiService.cancelTournament(id);
      
      // Refresh tournament data
      const response = await apiService.getTournament(id);
      setTournament(response.data);
      
      alert('Tournament cancelled successfully!');
    } catch (err) {
      console.error('Error cancelling tournament:', err);
      alert('Failed to cancel tournament. Please try again.');
    }
  };

  // Render loading state
  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '60vh' 
      }}>
        <CircularProgress sx={{ mb: 3 }} />
        <Typography>Loading tournament details...</Typography>
      </Box>
    );
  }

  // Render error state
  if (error) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '60vh' 
      }}>
        <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>
        <Button 
          variant="contained" 
          startIcon={<ArrowBackIcon />}
          onClick={() => history.push('/profile')}
        >
          Return to Dashboard
        </Button>
      </Box>
    );
  }

  // Get status color for badges
  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return 'warning';
      case 'in_progress': return 'info';
      case 'completed': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  // Format match result for display
  const formatMatchResult = (match) => {
  if (!match.result || match.result === 'pending' || match.result === '') return 'Pending';
  if (match.result === 'white_win') return `${match.white_bot_name || 'White'} won`;
  if (match.result === 'black_win') return `${match.black_bot_name || 'Black'} won`;
  if (match.result === 'draw') return 'Draw';
  if (match.result === 'timeout') return 'Timeout';
  if (match.result === 'error') {
    return match.error_message ? `Error: ${match.error_message}` : 'Error occurred';
  }
  return match.result || 'Unknown';
};

  return (
    <Box sx={{ py: 4, px: 2, maxWidth: 1200, mx: 'auto' }}>
      {/* Breadcrumb */}
      <Box sx={{ mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => history.push('/profile')}
          sx={{ mb: 2 }}
        >
          Back to Dashboard
        </Button>
      </Box>

      {/* Tournament Header */}
      <Paper elevation={3} sx={{ p: 3, borderRadius: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <Box>
            <Typography variant="h4" fontWeight={700}>{tournament.name}</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1, flexWrap: 'wrap' }}>
              <Chip 
                label={tournament.status.toUpperCase()} 
                color={getStatusColor(tournament.status)}
                size="small"
                sx={{ mr: 1, mb: 1 }}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mr: 2, mb: 1 }}>
                Created: {new Date(tournament.created_at).toLocaleDateString()}
              </Typography>
              {tournament.scheduled_at && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Scheduled: {new Date(tournament.scheduled_at).toLocaleString()}
                </Typography>
              )}
            </Box>
            {tournament.description && (
              <Typography sx={{ mt: 1 }}>
                {tournament.description}
              </Typography>
            )}
          </Box>
          <Box sx={{ display: 'flex', mt: 2, flexWrap: 'wrap' }}>
            {tournament.status === 'scheduled' && (
              <Button 
                variant="contained" 
                color="primary" 
                startIcon={<PlayArrowIcon />}
                onClick={startTournament}
                sx={{ mr: 1, mb: 1 }}
              >
                Start Tournament
              </Button>
            )}
            {(tournament.status === 'in_progress' || tournament.status === 'completed') && (
              <Button 
                variant="contained" 
                color="primary" 
                startIcon={<RefreshIcon />}
                onClick={recalculateScores}
                sx={{ mr: 1, mb: 1 }}
              >
                Recalculate Scores
              </Button>
            )}
            {tournament.status === 'in_progress' && (
              <Button 
                variant="outlined" 
                color="warning" 
                startIcon={<CancelIcon />}
                onClick={cancelTournament}
                sx={{ mr: 1, mb: 1 }}
              >
                Cancel Tournament
              </Button>
            )}
            <Button 
              variant="outlined" 
              color="error" 
              startIcon={<DeleteIcon />}
              onClick={() => setOpenDeleteModal(true)}
              sx={{ mb: 1 }}
            >
              Delete Tournament
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Participants Section */}
      <Paper elevation={3} sx={{ p: 3, borderRadius: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" fontWeight={700}>
            Participants
          </Typography>
          {tournament.status === 'scheduled' && (
            <Button 
              variant="contained" 
              color="primary" 
              startIcon={<AddIcon />}
              onClick={handleOpenAddBotModal}
            >
              Add Bot
            </Button>
          )}
        </Box>
        {participants.length === 0 ? (
          <Typography color="text.secondary">
            No bots in this tournament yet. Add bots using the button above.
          </Typography>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Rank</TableCell>
                  <TableCell>Bot Name</TableCell>
                  <TableCell>Owner</TableCell>
                  <TableCell>Score</TableCell>
                  {tournament.status === 'scheduled' && <TableCell align="right">Actions</TableCell>}
                </TableRow>
              </TableHead>
              <TableBody>
                {/* Sort participants by score in descending order */}
                {[...participants].sort((a, b) => b.score - a.score).map((participant, index) => (
                  <TableRow key={participant.bot_id}>
                    <TableCell>{index + 1}</TableCell>
                    <TableCell>{participant.bot_name}</TableCell>
                    <TableCell>{participant.owner_email}</TableCell>
                    <TableCell>{participant.score}</TableCell>
                    {tournament.status === 'scheduled' && (
                      <TableCell align="right">
                        <Button 
                          size="small" 
                          color="error" 
                          onClick={() => removeParticipant(participant.bot_id)}
                        >
                          Remove
                        </Button>
                      </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Matches Section */}
      <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
        <Typography variant="h5" fontWeight={700} sx={{ mb: 2 }}>
          Matches
        </Typography>
        {matches.length === 0 ? (
          <Typography color="text.secondary">
            No matches have been created yet.
            {tournament.status === 'scheduled' && ' Start the tournament to generate matches.'}
          </Typography>
        ) : (
            <Grid container spacing={2}>
            {matches.map(match => (
              <Grid item xs={12} md={6} key={match.id}>
                <Paper 
                  elevation={2} 
                  sx={{ 
                    p: 2, 
                    borderRadius: 2,
                    borderLeft: '4px solid',
                    borderColor: match.status === 'error' || match.result === 'error' ? 
                      'error.main' : 
                      match.status === 'completed' ? 
                      'success.main' : 'primary.main'
                  }}
                >
                  <Typography variant="h6">
                    {match.white_bot_name || 'Unknown'} vs {match.black_bot_name || 'Unknown'}
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2">
                      Status: <b>{match.status}</b>
                    </Typography>
                    <Typography variant="body2">
                      Result: <b>{formatMatchResult(match)}</b>
                    </Typography>
                    {match.round && (
                      <Typography variant="body2">
                        Round: {match.round}
                      </Typography>
                    )}
                    {match.error_message && (
                      <Typography variant="body2" color="error">
                        Error: {match.error_message}
                      </Typography>
                    )}
                  </Box>
                  <Box sx={{ display: 'flex', mt: 2 }}>
                    {match.pgn_file && match.pgn_file !== "" ? (
                      <Button 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                        component="a"
                        href={match.pgn_file.startsWith('http') ? match.pgn_file : `http://localhost:8000${match.pgn_file}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => {
                          // Stop the event if the URL is invalid
                          if (!match.pgn_file || match.pgn_file === "#") {
                            e.preventDefault();
                            alert("PGN file is not available for this match");
                          }
                        }}
                        sx={{ mr: 1 }}
                      >
                        View PGN
                      </Button>
                    ) : null}
                    
                    {match.log_file && match.log_file !== "" ? (
                      <Button 
                        size="small" 
                        color="secondary" 
                        variant="outlined"
                        component="a"
                        href={match.log_file.startsWith('http') ? match.log_file : `http://localhost:8000${match.log_file}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => {
                          // Stop the event if the URL is invalid
                          if (!match.log_file || match.log_file === "#") {
                            e.preventDefault();
                            alert("Log file is not available for this match");
                          }
                        }}
                      >
                        View Log
                      </Button>
                    ) : null}
                    
                    {(!match.pgn_file || match.pgn_file === "") && (!match.log_file || match.log_file === "") && (
                      <Typography variant="body2" color="text.secondary">
                        No files available for this match
                      </Typography>
                    )}
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>

      {/* Add Bot Modal */}
      <Dialog open={openAddBotModal} onClose={() => setOpenAddBotModal(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Bots to Tournament</DialogTitle>
        <DialogContent>
          {botError && <Alert severity="error" sx={{ mb: 2 }}>{botError}</Alert>}
          {botSuccess && <Alert severity="success" sx={{ mb: 2 }}>{botSuccess}</Alert>}
          
          <TextField
            fullWidth
            placeholder="Search bots by name or owner..."
            value={botSearch}
            onChange={(e) => setBotSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ mb: 2, mt: 1 }}
          />
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="body2">
              Select bots to add to the tournament (only active bots shown):
            </Typography>
            <Box>
              <Button 
                size="small" 
                onClick={toggleSelectAll}
                sx={{ mr: 1 }}
              >
                {selectedBots.length === filteredBots.length && filteredBots.length > 0 
                  ? 'Deselect All' 
                  : 'Select All'}
              </Button>
              <Chip 
                label={`${selectedBots.length} selected`} 
                size="small" 
                color={selectedBots.length > 0 ? "primary" : "default"}
              />
            </Box>
          </Box>
          
          {addingBots && <LinearProgress sx={{ mb: 2 }} />}
          
          {filteredBots.length === 0 ? (
            <Typography color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
              {availableBots.length === 0 
                ? 'No active bots available to add. All active bots are already in the tournament.'
                : 'No bots match your search criteria.'}
            </Typography>
          ) : (
            <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto', p: 1 }}>
              {filteredBots.map(bot => (
                <Box 
                  key={bot.id} 
                  sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    p: 1,
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                    backgroundColor: selectedBots.includes(bot.id) ? 'action.selected' : 'background.paper'
                  }}
                >
                  <Box>
                    <Typography fontWeight={500}>{bot.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Owner: {bot.owner_email}
                    </Typography>
                  </Box>
                  <Button
                    size="small"
                    color={selectedBots.includes(bot.id) ? "error" : "primary"}
                    onClick={() => toggleBotSelection(bot.id)}
                  >
                    {selectedBots.includes(bot.id) ? 'Remove' : 'Add'}
                  </Button>
                </Box>
              ))}
            </Paper>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddBotModal(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={addSelectedBots}
            disabled={selectedBots.length === 0 || addingBots}
          >
            {addingBots ? 'Adding...' : 'Add Selected Bots'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Tournament Modal */}
      <Dialog open={openDeleteModal} onClose={() => !deleting && setOpenDeleteModal(false)}>
        <DialogTitle>Delete Tournament</DialogTitle>
        <DialogContent>
          {deleteError && <Alert severity="error" sx={{ mb: 2 }}>{deleteError}</Alert>}
          {deleteSuccess && <Alert severity="success" sx={{ mb: 2 }}>{deleteSuccess}</Alert>}
          <Typography>
            Are you sure you want to permanently delete this tournament? This will remove all matches, results, and participant data. This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setOpenDeleteModal(false)} 
            disabled={deleting}
          >
            Cancel
          </Button>
          <Button 
            variant="contained" 
            color="error" 
            onClick={deleteTournament}
            disabled={deleting}
          >
            {deleting ? 'Deleting...' : 'Delete Tournament'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TournamentDetailsPage;