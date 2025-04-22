import React, { useEffect, useState } from 'react';
import {
  Box, Paper, Typography, Avatar, Divider, Button, Chip, Grid, Stack, CircularProgress,
  Tabs, Tab, TextField, InputAdornment, IconButton, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Tooltip, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import GroupIcon from '@mui/icons-material/Group';
import HomeIcon from '@mui/icons-material/Home';
import SearchIcon from '@mui/icons-material/Search';
import LeaderboardIcon from '@mui/icons-material/Leaderboard';
import AddIcon from '@mui/icons-material/Add';
import api from '../services/apiService';
import { useHistory } from 'react-router-dom';

function a11yProps(index) {
  return {
    id: `dashboard-tab-${index}`,
    'aria-controls': `dashboard-tabpanel-${index}`,
  };
}

const ProfilePage = ({ userData }) => {
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState(0);

  // Data states
  const [students, setStudents] = useState([]);
  const [tournaments, setTournaments] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);

  // Search states
  const [studentSearch, setStudentSearch] = useState('');
  const [tournamentSearch, setTournamentSearch] = useState('');
  const [leaderboardSearch, setLeaderboardSearch] = useState('');

  // Tournament creation modal state
  const [openCreate, setOpenCreate] = useState(false);
  const [createData, setCreateData] = useState({ name: '', description: '', scheduled_at: '' });
  const [createError, setCreateError] = useState('');
  const [creating, setCreating] = useState(false);

  const history = useHistory();

  // Fetch all data on mount
  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getStudents(),
      api.getTournaments(),
      api.getLeaderboard()
    ])
      .then(([studentsRes, tournamentsRes, leaderboardRes]) => {
        setStudents(studentsRes.data || []);
        setTournaments(tournamentsRes.data || []);
        setLeaderboard((leaderboardRes.data && leaderboardRes.data.leaderboard) || []);
      })
      .catch((err) => {
        console.error("Error fetching data", err);
        setStudents([]);
        setTournaments([]);
        setLeaderboard([]);
      })
      .finally(() => setLoading(false));
  }, []);

  // Filtering
  const filteredStudents = students.filter(
    s =>
      (s.name && s.name.toLowerCase().includes(studentSearch.toLowerCase())) ||
      (s.email && s.email.toLowerCase().includes(studentSearch.toLowerCase()))
  );

  const filteredTournaments = tournaments.filter(
    t =>
      (t.name && t.name.toLowerCase().includes(tournamentSearch.toLowerCase())) ||
      (t.description && t.description.toLowerCase().includes(tournamentSearch.toLowerCase()))
  );

  const filteredLeaderboard = leaderboard.filter(
    b =>
      (b.bot_name && b.bot_name.toLowerCase().includes(leaderboardSearch.toLowerCase())) ||
      (b.owner && b.owner.toLowerCase().includes(leaderboardSearch.toLowerCase()))
  );

  // Tournament creation handlers
  const handleCreateTournament = async () => {
    setCreating(true);
    setCreateError('');
    try {
      // Only include scheduled_at if set and valid
      const payload = {
        name: createData.name,
        description: createData.description,
      };
      if (createData.scheduled_at) {
        payload.scheduled_at = new Date(createData.scheduled_at).toISOString();
      }
      
      const response = await api.createTournament(payload);
      
      // Add the new tournament to the state
      setTournaments([...tournaments, response.data]);
      
      // Reset and close modal
      setOpenCreate(false);
      setCreateData({ name: '', description: '', scheduled_at: '' });
    } catch (err) {
      console.error("Error creating tournament", err);
      setCreateError(
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Failed to create tournament.'
      );
    } finally {
      setCreating(false);
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
                {userData.email ? userData.email[0].toUpperCase() : 'U'}
              </Avatar>
              <Typography variant="h5" fontWeight={700} sx={{ mb: 0.5 }}>
                {userData.name || userData.email}
              </Typography>
              <Chip
                label={userData.role ? userData.role.charAt(0).toUpperCase() + userData.role.slice(1) : 'Teacher'}
                color="primary"
                sx={{ fontWeight: 600, fontSize: '1rem', mb: 1 }}
              />
              <Typography variant="body2" color="text.secondary">
                Member since {userData.date_joined ? new Date(userData.date_joined).toLocaleDateString() : 'N/A'}
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
            </Stack>
          </Paper>
        </Grid>
        <Grid item xs={12} md={9}>
          <Typography variant="h4" fontWeight={800} color="primary" gutterBottom>
            Teacher Dashboard
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
            <Tab label="Manage Students" icon={<GroupIcon />} iconPosition="start" {...a11yProps(0)} />
            <Tab label="Manage Tournaments" icon={<EmojiEventsIcon />} iconPosition="start" {...a11yProps(1)} />
            <Tab label="Leaderboard" icon={<LeaderboardIcon />} iconPosition="start" {...a11yProps(2)} />
          </Tabs>
          {/* Students Tab */}
          {tab === 0 && (
            <Box>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                Students
              </Typography>
              <TextField
                placeholder="Search students..."
                value={studentSearch}
                onChange={e => setStudentSearch(e.target.value)}
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
              <Box sx={{ mt: 2 }}>
                {filteredStudents.length === 0 ? (
                  <Typography color="text.secondary">No students found.</Typography>
                ) : (
                  filteredStudents.map(student => (
                    <Paper
                      key={student.id}
                      sx={{
                        p: 2,
                        mb: 2,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        borderRadius: 3,
                        boxShadow: '0 2px 12px rgba(33,150,243,0.08)',
                      }}
                    >
                      <Box>
                        <Typography fontWeight={700}>{student.name || student.email}</Typography>
                        <Typography color="text.secondary" fontSize={14}>
                          {student.email}
                        </Typography>
                        <Typography color="text.secondary" fontSize={13}>
                          Bots: {student.bot_count ?? student.bots ?? '-'} • Joined: {student.date_joined ? new Date(student.date_joined).toLocaleDateString() : student.joined || '-'}
                        </Typography>
                      </Box>
                      <Tooltip title="View Details">
                        <IconButton color="primary" size="large" onClick={() => history.push(`/student/${student.id}`)}>
                          <SchoolIcon />
                        </IconButton>
                      </Tooltip>
                    </Paper>
                  ))
                )}
              </Box>
            </Box>
          )}
          {/* Tournaments Tab */}
          {tab === 1 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
                <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={() => setOpenCreate(true)}>
                  Create Tournament
                </Button>
              </Box>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                Tournaments
              </Typography>
              <TextField
                placeholder="Search tournaments..."
                value={tournamentSearch}
                onChange={e => setTournamentSearch(e.target.value)}
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
              <Box sx={{ mt: 2 }}>
                {filteredTournaments.length === 0 ? (
                  <Typography color="text.secondary">No tournaments found.</Typography>
                ) : (
                  filteredTournaments.map(tournament => (
                    <Paper
                      key={tournament.id}
                      sx={{
                        p: 2,
                        mb: 2,
                        borderRadius: 3,
                        boxShadow: '0 2px 12px rgba(156,39,176,0.08)',
                      }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box>
                          <Typography fontWeight={700}>{tournament.name}</Typography>
                          <Typography color="text.secondary" fontSize={14}>
                            {tournament.description}
                          </Typography>
                          <Typography color="text.secondary" fontSize={13}>
                            Status: <b>{tournament.status}</b> • Participants: {tournament.participant_count ?? tournament.participants ?? '-'} • Matches: {tournament.match_count ?? tournament.matches ?? '-'}
                          </Typography>
                          <Typography color="text.secondary" fontSize={13}>
                            Created: {tournament.created_at ? new Date(tournament.created_at).toLocaleDateString() : tournament.created || '-'} • Scheduled: {tournament.scheduled_at ? new Date(tournament.scheduled_at).toLocaleString() : tournament.scheduled || '-'}
                          </Typography>
                        </Box>
                        <Stack direction="row" spacing={1}>
                        <Button 
                            variant="outlined" 
                            color="primary" 
                            size="small" 
                            onClick={() => history.push(`/tournament/${tournament.id}`)}
                            >
                            Manage
                            </Button>
                          <Button 
                            variant="outlined" 
                            color="error" 
                            size="small"
                            onClick={async () => {
                              if (window.confirm(`Are you sure you want to delete tournament "${tournament.name}"?`)) {
                                try {
                                  await api.deleteTournament(tournament.id);
                                  setTournaments(tournaments.filter(t => t.id !== tournament.id));
                                } catch (err) {
                                  console.error("Error deleting tournament", err);
                                  alert("Failed to delete tournament");
                                }
                              }
                            }}
                          >
                            Delete
                          </Button>
                        </Stack>
                      </Box>
                    </Paper>
                  ))
                )}
              </Box>
              {/* Create Tournament Modal */}
              <Dialog open={openCreate} onClose={() => setOpenCreate(false)}>
                <DialogTitle>Create New Tournament</DialogTitle>
                <DialogContent>
                  <TextField
                    label="Tournament Name"
                    value={createData.name}
                    onChange={e => setCreateData({ ...createData, name: e.target.value })}
                    fullWidth
                    margin="normal"
                    required
                  />
                  <TextField
                    label="Description"
                    value={createData.description}
                    onChange={e => setCreateData({ ...createData, description: e.target.value })}
                    fullWidth
                    margin="normal"
                    multiline
                    rows={2}
                  />
                  <TextField
                    label="Schedule"
                    type="datetime-local"
                    value={createData.scheduled_at}
                    onChange={e => setCreateData({ ...createData, scheduled_at: e.target.value })}
                    fullWidth
                    margin="normal"
                    InputLabelProps={{ shrink: true }}
                  />
                  {createError && <Typography color="error">{createError}</Typography>}
                </DialogContent>
                <DialogActions>
                  <Button onClick={() => setOpenCreate(false)}>Cancel</Button>
                  <Button onClick={handleCreateTournament} disabled={creating || !createData.name} variant="contained">
                    {creating ? 'Creating...' : 'Create'}
                  </Button>
                </DialogActions>
              </Dialog>
            </Box>
          )}
          {/* Leaderboard Tab */}
          {tab === 2 && (
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
                      <TableCell>Tournaments</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredLeaderboard.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={10} align="center">
                          No bots found.
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredLeaderboard.map((bot, idx) => (
                        <TableRow key={bot.id || bot.rank || idx}>
                          <TableCell>
                            <b>{bot.rank ?? idx + 1}</b>
                          </TableCell>
                          <TableCell>{bot.name || bot.bot_name}</TableCell>
                          <TableCell>{bot.owner}</TableCell>
                          <TableCell>{bot.win_percentage ?? bot.win ?? '-'}</TableCell>
                          <TableCell>{bot.draw_percentage ?? bot.draw ?? '-'}</TableCell>
                          <TableCell>{bot.total_games ?? bot.games ?? '-'}</TableCell>
                          <TableCell>{bot.wins}</TableCell>
                          <TableCell>{bot.draws}</TableCell>
                          <TableCell>{bot.losses}</TableCell>
                          <TableCell>{bot.tournament_participations ?? bot.tournaments ?? '-'}</TableCell>
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
    </Box>
  );
};

export default ProfilePage;