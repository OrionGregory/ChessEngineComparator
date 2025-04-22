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
        backgroundColor: theme.palette.grey[100],
        py: { xs: 4, md: 8 },
        px: 2,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          maxWidth: 900,
          mx: 'auto',
          p: { xs: 3, md: 6 },
          borderRadius: 4,
          backgroundColor: '#ffffff',
        }}
      >
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <Typography
            variant="h4"
            fontWeight={700}
            color="primary"
            sx={{ mb: 1 }}
          >
            Chess Bot Tournament
          </Typography>
          <Chip
            icon={<SmartToyIcon />}
            label={`Logged in as: ${userData?.email || 'Guest'}`}
            sx={{
              fontWeight: 500,
              backgroundColor: theme.palette.grey[200],
              color: theme.palette.text.primary,
            }}
          />
        </Box>

        <Divider sx={{ mb: 4 }} />

        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Typography variant="h5" fontWeight={600} gutterBottom>
              Platform Overview
            </Typography>
            <Typography color="text.secondary" sx={{ mb: 2 }}>
              Create, test, and compete with chess bots in a structured, competitive environment.
            </Typography>

            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <EmojiEventsIcon color="primary" sx={{ mr: 1 }} />
              <Typography>Compete in tournaments</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <SmartToyIcon color="primary" sx={{ mr: 1 }} />
              <Typography>Build and train your chess bot</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <GroupIcon color="primary" sx={{ mr: 1 }} />
              <Typography>Collaborate and learn with peers</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <SchoolIcon color="primary" sx={{ mr: 1 }} />
              <Typography>Track your progress and achievements</Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            {userData?.role === 'teacher' ? (
              <Box
                sx={{
                  p: 3,
                  bgcolor: theme.palette.grey[100],
                  borderRadius: 2,
                  border: `1px solid ${theme.palette.divider}`,
                }}
              >
                <Typography variant="h6" fontWeight={600} color="primary" gutterBottom>
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
                  variant="outlined"
                  color="primary"
                  sx={{ mt: 2 }}
                  onClick={() => history.push('/profile')}
                >
                  Go to Dashboard
                </Button>
              </Box>
            ) : userData?.role === 'student' ? (
              <Box
                sx={{
                  p: 3,
                  bgcolor: theme.palette.grey[100],
                  borderRadius: 2,
                  border: `1px solid ${theme.palette.divider}`,
                }}
              >
                <Typography variant="h6" fontWeight={600} color="primary" gutterBottom>
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
                  variant="outlined"
                  color="primary"
                  onClick={() => history.push('/profile')}
                  sx={{ mt: 2 }}
                >
                  Go to Dashboard
                </Button>
              </Box>
            ) : (
              <Box
                sx={{
                  p: 3,
                  bgcolor: theme.palette.grey[100],
                  borderRadius: 2,
                  border: `1px solid ${theme.palette.divider}`,
                }}
              >
                <Typography variant="h6" fontWeight={600} color="primary" gutterBottom>
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
