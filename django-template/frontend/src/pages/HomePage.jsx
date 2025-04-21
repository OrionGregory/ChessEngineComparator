import React from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Button, 
  Grid, 
  useTheme, 
  useMediaQuery 
} from '@mui/material';
import { styled } from '@mui/system';
import { Link } from 'react-router-dom';
import ChessIcon from '@mui/icons-material/Casino';
import DashboardIcon from '@mui/icons-material/Dashboard';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import CodeIcon from '@mui/icons-material/Code';

const WelcomeBanner = styled(Box)(({ theme }) => ({
  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
  padding: theme.spacing(4),
  borderRadius: theme.shape.borderRadius,
  color: theme.palette.primary.contrastText,
  marginBottom: theme.spacing(4),
  boxShadow: theme.shadows[3],
  textAlign: 'center',
}));

const FeatureCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  textAlign: 'center',
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[2],
  transition: 'transform 0.3s ease-in-out',
  '&:hover': {
    transform: 'translateY(-5px)',
    boxShadow: theme.shadows[4],
  },
}));

const HomePage = ({ userData }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Container maxWidth="lg">
      <WelcomeBanner>
        <Typography variant={isMobile ? 'h4' : 'h3'} component="h1" gutterBottom>
          Welcome to Chess Bot Tournament Platform
        </Typography>
        <Typography variant="subtitle1">
          Create, test, and compete with your chess bots against others!
        </Typography>
        {userData && (
          <Typography variant="h6" mt={2}>
            Hello, {userData.email}! You are logged in as a{' '}
            <strong>{userData.role}</strong>.
          </Typography>
        )}
      </WelcomeBanner>

      <Grid container spacing={4}>
        <Grid item xs={12} sm={6} md={4}>
          <FeatureCard>
            <ChessIcon color="primary" sx={{ fontSize: 50 }} />
            <Typography variant="h6" mt={2}>
              Create Chess Bots
            </Typography>
            <Typography variant="body2" mt={1}>
              Design and train your own chess bots to compete in tournaments.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              component={Link}
              to="/create-bot"
              sx={{ mt: 2 }}
            >
              Get Started
            </Button>
          </FeatureCard>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <FeatureCard>
            <DashboardIcon color="secondary" sx={{ fontSize: 50 }} />
            <Typography variant="h6" mt={2}>
              Manage Classes
            </Typography>
            <Typography variant="body2" mt={1}>
              Teachers can create and manage classes for their students.
            </Typography>
            <Button
              variant="contained"
              color="secondary"
              component={Link}
              to="/teacher-dashboard"
              sx={{ mt: 2 }}
            >
              View Dashboard
            </Button>
          </FeatureCard>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <FeatureCard>
            <EmojiEventsIcon color="success" sx={{ fontSize: 50 }} />
            <Typography variant="h6" mt={2}>
              Compete in Tournaments
            </Typography>
            <Typography variant="body2" mt={1}>
              Participate in tournaments and see how your bot performs.
            </Typography>
            <Button
              variant="contained"
              color="success"
              component={Link}
              to="/tournaments"
              sx={{ mt: 2 }}
            >
              Join Now
            </Button>
          </FeatureCard>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <FeatureCard>
            <CodeIcon color="info" sx={{ fontSize: 50 }} />
            <Typography variant="h6" mt={2}>
              Review Code
            </Typography>
            <Typography variant="body2" mt={1}>
              Teachers can review and provide feedback on student code.
            </Typography>
            <Button
              variant="contained"
              color="info"
              component={Link}
              to="/review-code"
              sx={{ mt: 2 }}
            >
              Learn More
            </Button>
          </FeatureCard>
        </Grid>
      </Grid>
    </Container>
  );
};

export default HomePage;