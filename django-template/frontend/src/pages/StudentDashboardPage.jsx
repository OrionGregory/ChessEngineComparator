import React, { useState, useEffect } from 'react';
import {
  Box, Paper, Typography, Avatar, Divider, Button, Stack, CircularProgress,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Select,
  FormControl, InputLabel, Tabs, Tab, Grid, Chip, Card, CardContent, CardActions,
  InputAdornment, Alert, Snackbar
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import LeaderboardIcon from '@mui/icons-material/Leaderboard';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import HomeIcon from '@mui/icons-material/Home';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ArchiveIcon from '@mui/icons-material/Archive';
import EditIcon from '@mui/icons-material/Edit';
import { useHistory } from 'react-router-dom';
import apiService from '../services/apiService';

function a11yProps(index) {
  return {
    id: `student-tab-${index}`,
    'aria-controls': `student-tabpanel-${index}`,
  };
}

const StudentDashboardPage = ({ userData }) => {
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState(0);
  const [myBots, setMyBots] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [botSearch, setBotSearch] = useState('');
  const [leaderboardSearch, setLeaderboardSearch] = useState('');
  const history = useHistory();

  // Bot upload/edit/delete state
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedBot, setSelectedBot] = useState(null);
  const [botFile, setBotFile] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    visibility: 'private',
    status: 'draft'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  // Fetch data on component mount
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch student's bots
        const botsResponse = await apiService.getBots();
        setMyBots(botsResponse.data || []);
        
        // Try to fetch leaderboard
        try {
          const leaderboardResponse = await apiService.getLeaderboard();
          console.log("Leaderboard response:", leaderboardResponse.data);
          
          // Handle different response formats
          const leaderboardData = leaderboardResponse.data?.leaderboard || 
                                leaderboardResponse.data || [];
          setLeaderboard(leaderboardData);
        } catch (leaderboardError) {
          console.error('Leaderboard fetch error:', leaderboardError);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        showSnackbar('Failed to load data', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filtered lists based on search terms
  const filteredBots = myBots.filter(
    bot => bot.name?.toLowerCase().includes(botSearch.toLowerCase()) ||
           (bot.description && bot.description.toLowerCase().includes(botSearch.toLowerCase()))
  );

  const filteredLeaderboard = leaderboard.filter(
    entry => (entry.bot_name && entry.bot_name.toLowerCase().includes(leaderboardSearch.toLowerCase())) ||
             (entry.owner && entry.owner.toLowerCase().includes(leaderboardSearch.toLowerCase()))
  );

  // Snackbar helper
  const showSnackbar = (message, severity = 'success') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  // Bot management handlers
  const handleFileChange = (event) => {
    setBotFile(event.target.files[0]);
  };

  const handleCreateBot = async () => {
    if (!botFile) {
      setError('Please select a file to upload');
      return;
    }
  
    if (!formData.name) {
      setError('Bot name is required');
      return;
    }
  
    try {
      const data = new FormData();
      data.append('file_path', botFile); // IMPORTANT: Change 'file' to 'file_path' to match the backend
      data.append('name', formData.name);
      data.append('description', formData.description);
      data.append('visibility', formData.visibility);
      data.append('status', formData.status);
  
      const response = await apiService.createBot(data);
  
      setMyBots([...myBots, response.data]);
      setSuccess('Bot successfully uploaded!');
      
      // Reset form and close dialog after success
      setTimeout(() => {
        setUploadDialogOpen(false);
        setFormData({ name: '', description: '', visibility: 'private', status: 'draft' });
        setBotFile(null);
        setSuccess('');
        setError('');
      }, 1500);
      
      showSnackbar('Bot successfully created!');
    } catch (err) {
      console.error('Error uploading bot:', err);
      setError(err.response?.data?.error || err.response?.data?.detail || 'Failed to upload bot');
    }
  };

  const handleEditBot = (bot) => {
    // Only allow editing draft bots
    if (bot.status !== 'draft') {
      showSnackbar('Only draft bots can be edited', 'warning');
      return;
    }
    
    setSelectedBot(bot);
    setFormData({
      name: bot.name,
      description: bot.description || '',
      visibility: bot.visibility,
      status: bot.status
    });
    setEditDialogOpen(true);
    setError('');
  };

  const submitBotEdit = async () => {
    try {
      const response = await apiService.updateBot(selectedBot.id, formData);
      
      // Update bot in the local state
      setMyBots(myBots.map(bot => bot.id === selectedBot.id ? response.data : bot));
      setSuccess('Bot updated successfully!');
      
      // Close dialog after success
      setTimeout(() => {
        setEditDialogOpen(false);
        setSuccess('');
        setError('');
      }, 1500);
      
      showSnackbar('Bot updated successfully!');
    } catch (err) {
      console.error('Error updating bot:', err);
      setError(err.response?.data?.error || err.response?.data?.detail || 'Failed to update bot');
    }
  };

  const handleStatusChange = async (bot, newStatus) => {
    // Enforce status transition rules
    if (bot.status === 'draft' && newStatus !== 'active') {
      showSnackbar('Draft bots can only be activated', 'error');
      return;
    }
    
    if (bot.status === 'active' && newStatus !== 'archived') {
      showSnackbar('Active bots can only be archived', 'error');
      return;
    }
    
    if (bot.status === 'archived') {
      showSnackbar('Archived bots cannot be modified', 'error');
      return;
    }
    
    try {
      let response;
      
      // Use the dedicated endpoints for activate/archive 
      if (newStatus === 'active') {
        response = await apiService.activateBot(bot.id);
      } else if (newStatus === 'archived') {
        response = await apiService.archiveBot(bot.id);
      } else {
        showSnackbar(`Invalid status transition: ${bot.status} -> ${newStatus}`, 'error');
        return;
      }
      
      console.log('Status change response:', response);
      
      // Update bot in the local state
      setMyBots(myBots.map(b => {
        if (b.id === bot.id) {
          return { ...b, status: newStatus };
        }
        return b;
      }));
      
      showSnackbar(`Bot ${newStatus === 'active' ? 'activated' : 'archived'} successfully!`);
    } catch (err) {
      console.error('Error updating bot status:', err);
      console.error('Response data:', err.response?.data);
      
      // Show appropriate error message
      if (err.response?.status === 403) {
        showSnackbar('Permission denied: You may not have rights to modify this bot', 'error');
      } else {
        showSnackbar(err.response?.data?.error || 'Failed to update bot status', 'error');
      }
    }
  };

  const handleDeleteBot = (bot) => {
    // Only allow deleting draft bots
    if (bot.status !== 'draft') {
      showSnackbar(`${bot.status.charAt(0).toUpperCase() + bot.status.slice(1)} bots cannot be deleted`, 'error');
      return;
    }
    
    setSelectedBot(bot);
    setDeleteDialogOpen(true);
    setError('');
  };

  const confirmDeleteBot = async () => {
    try {
      await apiService.deleteBot(selectedBot.id);
      
      // Remove the bot from local state
      setMyBots(myBots.filter(bot => bot.id !== selectedBot.id));
      setSuccess('Bot deleted successfully!');
      
      // Close dialog after success
      setTimeout(() => {
        setDeleteDialogOpen(false);
        setSuccess('');
      }, 1500);
      
      showSnackbar('Bot deleted successfully!');
    } catch (err) {
      console.error('Error deleting bot:', err);
      setError(err.response?.data?.error || err.response?.data?.detail || 'Failed to delete bot');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ py: 4, px: 2, minHeight: 'calc(100vh - 64px)', background: (theme) => `linear-gradient(135deg, ${theme.palette.background.default} 60%, ${theme.palette.primary.light} 100%)` }}>
      <Grid container spacing={4} sx={{ maxWidth: 1200, mx: 'auto' }}>
        <Grid item xs={12} md={3}>
          <Paper elevation={3} sx={{ p: 3, borderRadius: 4, height: '100%' }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Avatar
                sx={{ width: 80, height: 80, mb: 2, bgcolor: 'primary.main', fontSize: 32, fontWeight: 700 }}
              >
                {userData?.email ? userData.email[0].toUpperCase() : 'S'}
              </Avatar>
              <Typography variant="h5" fontWeight={700} sx={{ mb: 0.5 }}>
                {userData?.name || userData?.email || 'Student'}
              </Typography>
              <Chip
                label={userData?.role ? userData.role.charAt(0).toUpperCase() + userData.role.slice(1) : 'Student'}
                color="primary"
                sx={{ fontWeight: 600, fontSize: '1rem', mb: 1 }}
              />
              <Typography variant="body2" color="text.secondary">
                Member since {userData?.date_joined ? new Date(userData.date_joined).toLocaleDateString() : 'N/A'}
              </Typography>
            </Box>
            <Divider sx={{ my: 2 }} />
            <Stack spacing={2} sx={{ width: '100%' }}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<HomeIcon />}
                sx={{ fontWeight: 600, borderRadius: 2 }}
                onClick={() => history.push('/')}
              >
                Home
              </Button>
              <Button
                variant="outlined"
                color="primary"
                startIcon={<CloudUploadIcon />}
                sx={{ fontWeight: 600, borderRadius: 2 }}
                onClick={() => {
                  setFormData({ name: '', description: '', visibility: 'private', status: 'draft' });
                  setBotFile(null);
                  setError('');
                  setSuccess('');
                  setUploadDialogOpen(true);
                }}
              >
                Upload New Bot
              </Button>
            </Stack>
          </Paper>
        </Grid>
        <Grid item xs={12} md={9}>
          <Typography variant="h4" fontWeight={800} color="primary" gutterBottom>
            Student Dashboard
          </Typography>
          <Tabs
            value={tab}
            onChange={(_, newValue) => setTab(newValue)}
            indicatorColor="primary"
            textColor="primary"
            sx={{ mb: 3 }}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="My Bots" icon={<SmartToyIcon />} iconPosition="start" {...a11yProps(0)} />
            <Tab label="Leaderboard" icon={<LeaderboardIcon />} iconPosition="start" {...a11yProps(1)} />
          </Tabs>
          
          {/* My Bots Tab */}
          {tab === 0 && (
            <Box>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                My Chess Bots
              </Typography>
                            
              <TextField
                placeholder="Search bots..."
                value={botSearch}
                onChange={e => setBotSearch(e.target.value)}
                size="small"
                sx={{ mb: 2, width: '100%', maxWidth: 350 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
              
              {filteredBots.length === 0 ? (
                <Paper sx={{ p: 3, borderRadius: 3, textAlign: 'center' }}>
                  <SmartToyIcon sx={{ fontSize: 60, color: 'text.secondary', opacity: 0.5, mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    No chess bots yet
                  </Typography>
                  <Typography color="text.secondary" sx={{ mb: 2 }}>
                    Upload your first chess bot to start participating in tournaments
                  </Typography>
                  <Button 
                    variant="contained" 
                    color="primary" 
                    startIcon={<CloudUploadIcon />}
                    onClick={() => {
                      setFormData({ name: '', description: '', visibility: 'private', status: 'draft' });
                      setBotFile(null);
                      setError('');
                      setSuccess('');
                      setUploadDialogOpen(true);
                    }}
                  >
                    Upload Bot
                  </Button>
                </Paper>
              ) : (
                <Grid container spacing={2}>
                  {filteredBots.map(bot => (
                    <Grid item xs={12} md={6} key={bot.id}>
                      <Card sx={{ 
                        borderRadius: 4,
                        boxShadow: theme => `0 4px 20px rgba(0,0,0,${theme.palette.mode === 'dark' ? 0.5 : 0.1})`,
                        opacity: bot.status === 'archived' ? 0.7 : 1
                      }}>
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <Typography variant="h6" fontWeight={700}>{bot.name}</Typography>
                            <Chip
                              label={bot.status.toUpperCase()}
                              color={
                                bot.status === 'active' ? 'success' :
                                bot.status === 'draft' ? 'warning' : 'default'
                              }
                              size="small"
                            />
                          </Box>
                          <Typography color="text.secondary" sx={{ mt: 1, mb: 2 }}>
                            {bot.description || 'No description provided'}
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                            <Chip
                              label={`Visibility: ${bot.visibility.charAt(0).toUpperCase() + bot.visibility.slice(1)}`}
                              size="small"
                              variant="outlined"
                            />
                            {bot.tournament_count > 0 && (
                              <Chip
                                label={`${bot.tournament_count} Tournaments`}
                                size="small"
                                variant="outlined"
                              />
                            )}
                          </Box>
                          <Typography variant="body2" color="text.secondary">
                            Uploaded: {new Date(bot.created_at).toLocaleDateString()}
                          </Typography>
                        </CardContent>

                        <CardActions sx={{ px: 2, pb: 2, display: 'flex', flexWrap: 'wrap' }}>
                          {bot.status === 'draft' && (
                            <>
                              <Button 
                                size="small" 
                                color="primary"
                                startIcon={<EditIcon />} 
                                onClick={() => handleEditBot(bot)}
                                sx={{ mr: 1, mb: 1 }}
                              >
                                Edit
                              </Button>
                              <Button 
                                size="small" 
                                color="success"
                                startIcon={<CheckCircleIcon />} 
                                onClick={() => handleStatusChange(bot, 'active')}
                                sx={{ mr: 1, mb: 1 }}
                              >
                                Activate
                              </Button>
                              <Button 
                                size="small" 
                                color="error"
                                startIcon={<DeleteIcon />} 
                                onClick={() => handleDeleteBot(bot)}
                                sx={{ mb: 1 }}
                              >
                                Delete
                              </Button>
                            </>
                          )}
                          
                          {bot.status === 'active' && (
                            <Button 
                              size="small" 
                              color="warning"
                              startIcon={<ArchiveIcon />} 
                              onClick={() => handleStatusChange(bot, 'archived')}
                              sx={{ mr: 1, mb: 1 }}
                            >
                              Archive
                            </Button>
                          )}
                          
                          {bot.status === 'archived' && (
                            <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                              This bot is archived and cannot be modified
                            </Typography>
                          )}
                        </CardActions>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}
            </Box>
          )}
          
          {/* Leaderboard Tab */}
          {tab === 1 && (
            <Box>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                Bot Leaderboard
              </Typography>
              <TextField
                placeholder="Search bots or owners..."
                value={leaderboardSearch}
                onChange={e => setLeaderboardSearch(e.target.value)}
                size="small"
                sx={{ mb: 2, width: '100%', maxWidth: 350 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
              <TableContainer component={Paper} sx={{ borderRadius: 3, boxShadow: '0 2px 12px rgba(33,150,243,0.08)' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Rank</TableCell>
                      <TableCell>Bot Name</TableCell>
                      <TableCell>Owner</TableCell>
                      <TableCell>Win %</TableCell>
                      <TableCell>Draw %</TableCell>
                      <TableCell>Games</TableCell>
                      <TableCell>Wins</TableCell>
                      <TableCell>Draws</TableCell>
                      <TableCell>Losses</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredLeaderboard.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={9} align="center">
                          No bots found.
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredLeaderboard.map((bot, idx) => (
                        <TableRow key={bot.id || idx} sx={{
                          backgroundColor: bot.owner === userData?.email ? 'rgba(25, 118, 210, 0.08)' : 'inherit'
                        }}>
                          <TableCell>
                            <b>{bot.rank || idx + 1}</b>
                          </TableCell>
                          <TableCell>{bot.bot_name || bot.name}</TableCell>
                          <TableCell>{bot.owner}</TableCell>
                          <TableCell>{bot.win_percentage || bot.win || '-'}</TableCell>
                          <TableCell>{bot.draw_percentage || bot.draw || '-'}</TableCell>
                          <TableCell>{bot.total_games || bot.games || '-'}</TableCell>
                          <TableCell>{bot.wins || '-'}</TableCell>
                          <TableCell>{bot.draws || '-'}</TableCell>
                          <TableCell>{bot.losses || '-'}</TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </Grid>
      </Grid>
      
      {/* Upload Bot Dialog */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Chess Bot</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
          )}
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>
          )}
          <TextField
            label="Bot Name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            fullWidth
            margin="normal"
            required
          />
          <TextField
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            fullWidth
            margin="normal"
            multiline
            rows={3}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Visibility</InputLabel>
            <Select
              value={formData.visibility}
              onChange={(e) => setFormData({...formData, visibility: e.target.value})}
              label="Visibility"
            >
              <MenuItem value="private">Private</MenuItem>
              <MenuItem value="public">Public</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Status</InputLabel>
            <Select
              value={formData.status}
              onChange={(e) => setFormData({...formData, status: e.target.value})}
              label="Status"
            >
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="active">Active</MenuItem>
            </Select>
          </FormControl>
          <Box sx={{ mt: 2 }}>
            <input
              accept=".py"  // Restrict to only Python files
              id="bot-file-upload"
              type="file"
              name="file_path"  // Ensure this matches backend
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            <label htmlFor="bot-file-upload">
              <Button
                variant="outlined"
                component="span"
                startIcon={<CloudUploadIcon />}
                sx={{ mt: 1 }}
              >
                {botFile ? botFile.name : 'Select Bot File (.py)'}
              </Button>
            </label>
            {botFile && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Selected file: {botFile.name}
              </Typography>
            )}
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
              Please upload a Python (.py) file with your chess bot implementation. Maximum size: 5MB.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateBot} 
            variant="contained" 
            color="primary"
            disabled={!formData.name || !botFile}
          >
            Upload
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Edit Bot Dialog - only for draft bots */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Bot</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
          )}
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>
          )}
          <TextField
            label="Bot Name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            fullWidth
            margin="normal"
            required
          />
          <TextField
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            fullWidth
            margin="normal"
            multiline
            rows={3}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Visibility</InputLabel>
            <Select
              value={formData.visibility}
              onChange={(e) => setFormData({...formData, visibility: e.target.value})}
              label="Visibility"
            >
              <MenuItem value="private">Private</MenuItem>
              <MenuItem value="public">Public</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={submitBotEdit} variant="contained" color="primary">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Delete Bot Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
          )}
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>
          )}
          <Typography>
            Are you sure you want to delete the bot "{selectedBot?.name}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={confirmDeleteBot} variant="contained" color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={() => setSnackbarOpen(false)} 
          severity={snackbarSeverity} 
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default StudentDashboardPage;