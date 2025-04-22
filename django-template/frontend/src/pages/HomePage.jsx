import React from 'react';
import { useHistory } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Button,
  Divider,
  Grid,
  useTheme,
  Chip,
} from '@mui/material';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import SchoolIcon from '@mui/icons-material/School';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import GroupIcon from '@mui/icons-material/Group';


const HomePage = ({ userData }) => {
    const history = useHistory();
  const theme = useTheme();

  return (
    <Box
      sx={{
        minHeight: 'calc(100vh - 64px)',
        background: `linear-gradient(135deg, ${theme.palette.background.default} 60%, ${theme.palette.primary.light} 100%)`,
        py: { xs: 4, md: 8 },
        px: 2,
      }}
    >
      <Paper
        elevation={6}
        sx={{
          maxWidth: 900,
          mx: 'auto',
          p: { xs: 3, md: 6 },
          borderRadius: 5,
          background: `linear-gradient(120deg, #fff 80%, ${theme.palette.primary.light} 100%)`,
          boxShadow: '0 8px 32px rgba(0,0,0,0.10)',
        }}
      >
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <Typography
            variant="h3"
            fontWeight={800}
            color="primary"
            sx={{
              letterSpacing: 1,
              mb: 1,
              textShadow: '1px 1px 8px rgba(25, 118, 210, 0.08)',
            }}
          >
            Welcome to Chess Bot Tournament
          </Typography>
          <Chip
            icon={<SmartToyIcon />}
            label={`Logged in as: ${userData?.email || 'Guest'}`}
            color="secondary"
            sx={{ fontWeight: 600, fontSize: '1rem', mt: 1 }}
          />
        </Box>
        <Divider sx={{ mb: 4 }} />
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Box sx={{ mb: 3 }}>
              <Typography variant="h5" fontWeight={700} gutterBottom>
                Platform Overview
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 2 }}>
                This platform allows students to create, test, and compete with chess bots in a fun and interactive environment.
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <EmojiEventsIcon color="primary" sx={{ mr: 1 }} />
                <Typography>Compete in tournaments</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SmartToyIcon color="secondary" sx={{ mr: 1 }} />
                <Typography>Build and train your own chess bot</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <GroupIcon color="success" sx={{ mr: 1 }} />
                <Typography>Collaborate and learn with peers</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SchoolIcon color="warning" sx={{ mr: 1 }} />
                <Typography>Track your progress and achievements</Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            {userData?.role === 'teacher' ? (
              <Box
                sx={{
                  p: 3,
                  bgcolor: '#e3f2fd',
                  borderRadius: 3,
                  boxShadow: '0 2px 12px rgba(33,150,243,0.08)',
                  mb: 2,
                }}
              >
                <Typography variant="h6" fontWeight={700} color="primary" gutterBottom>
                  Teacher Dashboard
                </Typography>
                <Typography sx={{ mb: 1 }}>
                  As a teacher, you can:
                </Typography>
                <ul style={{ marginLeft: 20 }}>
                  <li>Create and manage classes</li>
                  <li>View student progress</li>
                  <li>Organize tournaments</li>
                  <li>Review student code</li>
                </ul>
                <Button
                  variant="contained"
                  color="primary"
                  sx={{ mt: 2, fontWeight: 600, borderRadius: 2 }}
                  onClick={() => history.push('/profile')}
                >
                  Go to Dashboard
                </Button>
              </Box>
            ) : userData?.role === 'student' ? (
              <Box
                sx={{
                  p: 3,
                  bgcolor: '#f3e5f5',
                  borderRadius: 3,
                  boxShadow: '0 2px 12px rgba(156,39,176,0.08)',
                  mb: 2,
                }}
              >
                <Typography variant="h6" fontWeight={700} color="secondary" gutterBottom>
                  Student Dashboard
                </Typography>
                <Typography sx={{ mb: 1 }}>
                  As a student, you can:
                </Typography>
                <ul style={{ marginLeft: 20 }}>
                  <li>Create and train your chess bot</li>
                  <li>Test your bot against built-in opponents</li>
                  <li>Compete in tournaments</li>
                  <li>View your progress and rankings</li>
                </ul>
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={() => history.push('/profile')}
                  sx={{ mt: 2, fontWeight: 600, borderRadius: 2 }}
                >
                  Go to Dashboard
                </Button>
              </Box>
            ) : (
              <Box
                sx={{
                  p: 3,
                  bgcolor: '#fffde7',
                  borderRadius: 3,
                  boxShadow: '0 2px 12px rgba(255,235,59,0.08)',
                  mb: 2,
                }}
              >
                <Typography variant="h6" fontWeight={700} color="warning.main" gutterBottom>
                  Welcome!
                </Typography>
                <Typography>
                  Please log in to access your dashboard and start competing!
                </Typography>
              </Box>
            )}
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default HomePage;