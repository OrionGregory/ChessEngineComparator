import React, { useState, useEffect, useMemo } from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import { 
  ThemeProvider, 
  createTheme, 
  CssBaseline, 
  Box,
  CircularProgress
} from '@mui/material';
import Typography from '@mui/material/Typography';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import TournamentList from './components/TournamentList';
import BotCard from './components/BotCard';
import MainLayout from './pages/MainLayout';
import axios from 'axios';

// Configure axios to include credentials
axios.defaults.withCredentials = true;
axios.defaults.baseURL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

axios.interceptors.request.use(
  config => {
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
};

function App() {
  const [mode, setMode] = useState(localStorage.getItem('themeMode') || 'light');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userData, setUserData] = useState(null);
  const [authError, setAuthError] = useState(null);

  useEffect(() => {
    localStorage.setItem('themeMode', mode);
  }, [mode]);

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await axios.get('/api/user-info/');
        setIsAuthenticated(response.data.isAuthenticated);
        setAuthError(null);

        if (response.data.isAuthenticated) {
          setUserData({
            email: response.data.email,
            role: response.data.role,
            id: response.data.id,
            name: response.data.name,
            avatar: response.data.avatar
          });
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        setAuthError('API Error: ' + (error.response?.data?.message || error.message));
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: {
            main: mode === 'light' ? '#1976d2' : '#90caf9',
          },
          secondary: {
            main: mode === 'light' ? '#dc004e' : '#f48fb1',
          },
          background: {
            default: mode === 'light' ? '#f5f5f5' : '#121212',
            paper: mode === 'light' ? '#ffffff' : '#1e1e1e',
          },
        },
        shape: {
          borderRadius: 8,
        },
        typography: {
          fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
          h4: {
            fontWeight: 600,
          },
        },
        components: {
          MuiButton: {
            styleOverrides: {
              root: {
                textTransform: 'none',
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                borderRadius: 12,
              },
            },
          },
        },
      }),
    [mode]
  );

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const ProtectedRoute = ({ children, ...rest }) => {
    if (isLoading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <CircularProgress />
        </Box>
      );
    }

    return (
      <Route
        {...rest}
        render={({ location }) =>
          isAuthenticated ? (
            children
          ) : (
            <Redirect
              to={{
                pathname: '/login',
                state: { from: location },
              }}
            />
          )
        }
      />
    );
  };

  if (isLoading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <CircularProgress />
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Switch>
          <Route path="/login">
            {isAuthenticated ? (
              <Redirect to="/" />
            ) : (
              <LoginPage toggleTheme={toggleTheme} mode={mode} authError={authError} />
            )}
          </Route>

          <ProtectedRoute path="/" exact>
            <MainLayout 
              title="Dashboard" 
              isAuthenticated={isAuthenticated} 
              userData={userData} 
              toggleTheme={toggleTheme} 
              mode={mode}
            >
              <HomePage userData={userData} />
            </MainLayout>
          </ProtectedRoute>
          
          <ProtectedRoute path="/tournaments">
            <MainLayout 
              title="Tournaments" 
              isAuthenticated={isAuthenticated} 
              userData={userData} 
              toggleTheme={toggleTheme} 
              mode={mode}
            >
              <TournamentList userRole={userData?.role} />
            </MainLayout>
          </ProtectedRoute>
          
          <ProtectedRoute path="/bots">
            <MainLayout 
              title="My Chess Bots" 
              isAuthenticated={isAuthenticated} 
              userData={userData} 
              toggleTheme={toggleTheme} 
              mode={mode}
            >
              <Box sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Your bots will appear here once you create them
                </Typography>
                {/* This would be a grid of BotCard components in a real implementation */}
                <Box sx={{ mt: 3, display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 3 }}>
                  <BotCard 
                    bot={{
                      id: 'example',
                      name: 'Example Bot',
                      description: 'This is an example bot card. Create your own bots to see them here.',
                      status: 'inactive',
                      updated_at: new Date().toISOString()
                    }}
                    onEdit={() => alert('Edit functionality would go here')}
                    onDelete={() => alert('Delete functionality would go here')}
                    onTest={() => alert('Test functionality would go here')}
                  />
                </Box>
              </Box>
            </MainLayout>
          </ProtectedRoute>
          
          <ProtectedRoute path="/profile">
            <MainLayout 
              title="User Profile" 
              isAuthenticated={isAuthenticated} 
              userData={userData} 
              toggleTheme={toggleTheme} 
              mode={mode}
            >
              <Box sx={{ p: 2 }}>
                <Typography variant="h6">
                  User: {userData?.name || userData?.email}
                </Typography>
                <Typography variant="body1">
                  Role: {userData?.role}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  Profile management features will be implemented here
                </Typography>
              </Box>
            </MainLayout>
          </ProtectedRoute>

          <Route path="*">
            <Redirect to="/" />
          </Route>
        </Switch>
      </Router>
    </ThemeProvider>
  );
}

export default App;