import React, { useEffect, useState } from 'react';
import {
  Box, Paper, Typography, Avatar, Divider, Button, Stack, CircularProgress,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Select,
  FormControl, InputLabel, Chip
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import api from '../services/apiService';
import { useParams, useHistory } from 'react-router-dom';

const StudentDetailPage = () => {
  const { studentId } = useParams();
  const history = useHistory();
  const [student, setStudent] = useState(null);
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  
  // Bot edit state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedBot, setSelectedBot] = useState(null);
  const [editFormData, setEditFormData] = useState({
    name: '',
    description: '',
    visibility: 'private',
    status: 'draft'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getStudent(studentId),
      api.getStudentBots(studentId)
    ])
      .then(([studentRes, botsRes]) => {
        setStudent(studentRes.data);
        setBots(botsRes.data);
      })
      .catch(err => {
        console.error("Error fetching student data", err);
        setStudent(null);
        setBots([]);
      })
      .finally(() => setLoading(false));
  }, [studentId]);

  const handleDeleteStudent = async () => {
    if (!window.confirm('Are you sure you want to delete this student? This action cannot be undone.')) return;
    setDeleting(true);
    try {
      await api.deleteStudent(studentId);
      history.push('/profile');
    } catch (err) {
      console.error("Error deleting student", err);
      alert('Failed to delete student. You may not have permission.');
    } finally {
      setDeleting(false);
    }
  };
  
  const handleEditBot = (bot) => {
    setSelectedBot(bot);
    setEditFormData({
      name: bot.name,
      description: bot.description || '',
      visibility: bot.visibility,
      status: bot.status
    });
    setEditDialogOpen(true);
    setError('');
    setSuccess('');
  };
  
  const handleDeleteBot = (bot) => {
    setSelectedBot(bot);
    setDeleteDialogOpen(true);
    setError('');
    setSuccess('');
  };
  
  const submitBotEdit = async () => {
    try {
      const response = await api.updateBot(selectedBot.id, editFormData);
      const updatedBot = response.data;
      
      // Update the bot in the local state
      setBots(bots.map(bot => 
        bot.id === updatedBot.id ? updatedBot : bot
      ));
      
      setSuccess('Bot updated successfully!');
      
      // Close dialog after success
      setTimeout(() => {
        setEditDialogOpen(false);
        setSuccess('');
      }, 1500);
    } catch (err) {
      console.error("Error updating bot", err);
      setError(err.response?.data?.error || 'Failed to update bot. Please try again.');
    }
  };
  
  const confirmDeleteBot = async () => {
    try {
      await api.deleteBot(selectedBot.id);
      
      // Remove the bot from the local state
      setBots(bots.filter(bot => bot.id !== selectedBot.id));
      
      setSuccess('Bot deleted successfully!');
      
      // Close dialog after success
      setTimeout(() => {
        setDeleteDialogOpen(false);
        setSuccess('');
      }, 1500);
    } catch (err) {
      console.error("Error deleting bot", err);
      setError(err.response?.data?.error || 'Failed to delete bot. Please try again.');
    }
  };

  if (loading || !student) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: 'calc(100vh - 64px)', py: 4, px: 2, background: (theme) => `linear-gradient(135deg, ${theme.palette.background.default} 60%, ${theme.palette.primary.light} 100%)` }}>
      <Paper elevation={6} sx={{ maxWidth: 900, mx: 'auto', p: { xs: 3, md: 6 }, borderRadius: 5 }}>
        <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
          <IconButton onClick={() => history.goBack()} color="primary">
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" fontWeight={800} color="primary">
            Student Details
          </Typography>
        </Stack>
        <Divider sx={{ mb: 3 }} />
        <Stack direction="row" spacing={3} alignItems="center" sx={{ mb: 3 }}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 70, height: 70, fontSize: 32, fontWeight: 700 }}>
            {student.name ? student.name[0].toUpperCase() : student.email[0].toUpperCase()}
          </Avatar>
          <Box>
            <Typography variant="h5" fontWeight={700}>{student.name || student.email}</Typography>
            <Typography color="text.secondary">{student.email}</Typography>
            <Typography color="text.secondary" fontSize={14}>
              Joined: {student.date_joined ? new Date(student.date_joined).toLocaleDateString() : '-'}
            </Typography>
            <Button
              variant="outlined"
              color="error"
              onClick={handleDeleteStudent}
              sx={{ mt: 2 }}
              disabled={deleting}
            >
              {deleting ? 'Deleting...' : 'Delete Student'}
            </Button>
          </Box>
        </Stack>
        <Divider sx={{ mb: 3 }} />
        
        <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>Bots</Typography>
        <TableContainer component={Paper} sx={{ borderRadius: 3, boxShadow: '0 2px 12px rgba(33,150,243,0.08)' }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Visibility</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {bots.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">No bots found.</TableCell>
                </TableRow>
              ) : (
                bots.map(bot => (
                  <TableRow key={bot.id}>
                    <TableCell>{bot.name}</TableCell>
                    <TableCell>{bot.description || '-'}</TableCell>
                    <TableCell>
                      <Chip 
                        label={bot.status.toUpperCase()} 
                        color={
                          bot.status === 'active' ? 'success' : 
                          bot.status === 'draft' ? 'warning' : 'default'
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{bot.visibility}</TableCell>
                    <TableCell>{bot.created_at ? new Date(bot.created_at).toLocaleDateString() : '-'}</TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={1}>
                        <IconButton color="primary" size="small" onClick={() => handleEditBot(bot)}>
                          <EditIcon />
                        </IconButton>
                        <IconButton color="error" size="small" onClick={() => handleDeleteBot(bot)}>
                          <DeleteIcon />
                        </IconButton>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
      
      {/* Edit Bot Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Bot</DialogTitle>
        <DialogContent>
          {error && (
            <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>
          )}
          {success && (
            <Typography color="success.main" sx={{ mb: 2 }}>{success}</Typography>
          )}
          <TextField
            label="Bot Name"
            value={editFormData.name}
            onChange={(e) => setEditFormData({...editFormData, name: e.target.value})}
            fullWidth
            margin="normal"
            required
          />
          <TextField
            label="Description"
            value={editFormData.description}
            onChange={(e) => setEditFormData({...editFormData, description: e.target.value})}
            fullWidth
            margin="normal"
            multiline
            rows={3}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Visibility</InputLabel>
            <Select
              value={editFormData.visibility}
              onChange={(e) => setEditFormData({...editFormData, visibility: e.target.value})}
              label="Visibility"
            >
              <MenuItem value="private">Private</MenuItem>
              <MenuItem value="public">Public</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Status</InputLabel>
            <Select
              value={editFormData.status}
              onChange={(e) => setEditFormData({...editFormData, status: e.target.value})}
              label="Status"
            >
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="archived">Archived</MenuItem>
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
            <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>
          )}
          {success && (
            <Typography color="success.main" sx={{ mb: 2 }}>{success}</Typography>
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
    </Box>
  );
};

export default StudentDetailPage;