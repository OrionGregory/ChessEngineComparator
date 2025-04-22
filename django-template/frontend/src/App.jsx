import React, { useState, useEffect, useMemo } from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box, CircularProgress } from '@mui/material';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import ProfilePage from './pages/ProfilePage';
import StudentDetailPage from './pages/StudentDetailPage';
import TournamentDetailsPage from './pages/TournamentDetailsPage';
import StudentDashboardPage from './pages/StudentDashboardPage'; // Add this import
import Header from './components/Header';
import axios from 'axios';

// Configure axios to include credentials
axios.defaults.withCredentials = true;
axios.defaults.baseURL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Add CSRF and JWT token to every request
axios.interceptors.request.use(
  config => {
    // CSRF
    const csrfToken = document.cookie.split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    // JWT
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

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
            avatar: response.data.avatar,
            is_staff: response.data.role === 'teacher',
            date_joined: response.data.date_joined,
          });
        }
      } catch (error) {
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
        {isAuthenticated && <Header userData={userData} />}
        <Switch>
          <Route path="/login">
            {isAuthenticated ? (
              <Redirect to="/" />
            ) : (
              <LoginPage toggleTheme={toggleTheme} mode={mode} authError={authError} />
            )}
          </Route>
          <Route exact path="/">
            {isAuthenticated ? (
              <HomePage userData={userData} />
            ) : (
              <Redirect to="/login" />
            )}
          </Route>
          <Route exact path="/profile">
            {isAuthenticated ? (
              userData?.role === 'teacher' ? (
                <ProfilePage userData={userData} />
              ) : (
                <StudentDashboardPage userData={userData} />
              )
            ) : (
              <Redirect to="/login" />
            )}
          </Route>
          <Route exact path="/dashboard">
            {isAuthenticated ? (
              userData?.role === 'teacher' ? (
                <ProfilePage userData={userData} />
              ) : (
                <StudentDashboardPage userData={userData} />
              )
            ) : (
              <Redirect to="/login" />
            )}
          </Route>
          <Route path="/student/:studentId">
            {isAuthenticated && userData?.role === 'teacher' ? (
              <StudentDetailPage />
            ) : (
              <Redirect to="/profile" />
            )}
          </Route>
          <Route path="/tournament/:id">
          {isAuthenticated ? (
            userData?.role === 'teacher' ? (
              <TournamentDetailsPage userData={userData} />
            ) : (
              <Redirect to="/" />
            )
          ) : (
            <Redirect to="/login" />
          )}
        </Route>
          <Route path="*">
            <Redirect to={isAuthenticated ? "/" : "/login"} />
          </Route>
        </Switch>
      </Router>
    </ThemeProvider>
  );
}

export default App;