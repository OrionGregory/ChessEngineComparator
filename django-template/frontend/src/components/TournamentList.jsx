import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  TablePagination,
  Chip,
  Button,
  IconButton,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert
} from '@mui/material';
import { styled } from '@mui/system';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import RemoveRedEyeIcon from '@mui/icons-material/RemoveRedEye';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import { useHistory } from 'react-router-dom';
import axios from 'axios';

const StatusChip = styled(Chip)(({ theme, status }) => {
  const colors = {
    upcoming: theme.palette.info.main,
    active: theme.palette.success.main,
    completed: theme.palette.warning.main,
    cancelled: theme.palette.error.main,
  };
  
  return {
    backgroundColor: colors[status] || theme.palette.primary.main,
    color: theme.palette.getContrastText(colors[status] || theme.palette.primary.main),
  };
});

const TournamentList = ({ userRole }) => {
  const [tournaments, setTournaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [search, setSearch] = useState('');
  const history = useHistory();

  useEffect(() => {
    const fetchTournaments = async () => {
      setLoading(true);
      try {
        const response = await axios.get('/api/tournaments/');
        setTournaments(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching tournaments:', err);
        setError('Failed to load tournaments. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchTournaments();
  }, []);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearchChange = (event) => {
    setSearch(event.target.value);
    setPage(0);
  };

  const handleViewTournament = (id) => {
    history.push(`/tournaments/${id}`);
  };

  const handleJoinTournament = async (id) => {
    try {
      await axios.post(`/api/tournaments/${id}/join/`);
      // Refresh tournaments after joining
      const response = await axios.get('/api/tournaments/');
      setTournaments(response.data);
    } catch (err) {
      console.error('Error joining tournament:', err);
      setError('Failed to join tournament. Please try again.');
    }
  };

  const filteredTournaments = tournaments.filter(tournament => 
    tournament.name.toLowerCase().includes(search.toLowerCase()) ||
    tournament.description.toLowerCase().includes(search.toLowerCase())
  );

  const emptyRows = page > 0 
    ? Math.max(0, (1 + page) * rowsPerPage - filteredTournaments.length) 
    : 0;

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5" component="h2">
          <EmojiEventsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Tournaments
        </Typography>
        
        {userRole === 'teacher' && (
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => history.push('/tournaments/create')}
          >
            Create Tournament
          </Button>
        )}
      </Box>
      
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search tournaments..."
          value={search}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <IconButton>
                  <FilterListIcon />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      </Box>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Tournament Name</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Start Date</TableCell>
                  <TableCell>End Date</TableCell>
                  <TableCell>Participants</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredTournaments
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((tournament) => (
                    <TableRow key={tournament.id}>
                      <TableCell component="th" scope="row">
                        <Typography variant="body1">{tournament.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {tournament.description}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <StatusChip 
                          label={tournament.status} 
                          status={tournament.status} 
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(tournament.start_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        {new Date(tournament.end_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        {tournament.participant_count || 0}
                      </TableCell>
                      <TableCell align="center">
                        <IconButton 
                          color="primary"
                          onClick={() => handleViewTournament(tournament.id)}
                        >
                          <RemoveRedEyeIcon />
                        </IconButton>
                        {tournament.status === 'upcoming' && !tournament.user_participated && (
                          <Button 
                            variant="outlined" 
                            size="small"
                            onClick={() => handleJoinTournament(tournament.id)}
                          >
                            Join
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                {emptyRows > 0 && (
                  <TableRow style={{ height: 53 * emptyRows }}>
                    <TableCell colSpan={6} />
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={filteredTournaments.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </>
      )}
    </Box>
  );
};

export default TournamentList;