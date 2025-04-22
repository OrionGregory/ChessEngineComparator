import axios from 'axios';

// Create an axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true, // This is essential for cookies to be sent
});

// Get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Request interceptor to add CSRF token to non-GET requests
api.interceptors.request.use(config => {
  if (config.method !== 'get') {
    config.headers['X-CSRFToken'] = getCookie('csrftoken');
  }
  return config;
});

export default {
  // Student endpoints
  getStudents: () => api.get('/users/api/students/'),
  getStudent: (id) => api.get(`/users/api/students/${id}/`),
  getStudentBots: (id) => api.get(`/users/api/students/${id}/bots/`),
  deleteStudent: (id) => api.delete(`/users/api/students/${id}/`),

  // Tournament endpoints
  getTournaments: () => api.get('/users/api/tournaments/'),
  getTournament: (id) => api.get(`/users/api/tournaments/${id}/`),
  createTournament: (data) => api.post('/users/api/tournaments/', data),
  deleteTournament: (id) => api.post(`/users/api/tournaments/${id}/delete_tournament/`),
  addParticipant: (id, botId) => api.post(`/users/api/tournaments/${id}/add_participant/`, { bot_id: botId }),
  removeParticipant: (id, botId) => api.post(`/users/api/tournaments/${id}/remove_participant/`, { bot_id: botId }),
  startTournament: (id, options) => api.post(`/users/api/tournaments/${id}/start_tournament/`, options),
  cancelTournament: (id) => api.post(`/users/api/tournaments/${id}/cancel/`),

  // Bot endpoints
  getBots: () => api.get('/users/api/bots/'),
  getBot: (id) => api.get(`/users/api/bots/${id}/`),
  createBot: (data) => api.post('/users/api/bots/', data),
  updateBot: (id, data) => api.put(`/users/api/bots/${id}/`, data),
  deleteBot: (id) => api.delete(`/users/api/bots/${id}/`),
  
  // Leaderboard endpoint
  getLeaderboard: (tournamentId) => api.get(`/users/api/leaderboard/${tournamentId ? `?tournament=${tournamentId}` : ''}`),

  // Authentication status
  getAuthStatus: () => api.get('/users/api/auth-status/'),

  // User info - make sure to use the correct endpoint
  getUserInfo: () => api.get('/api/user-info/'),


  activateBot: (botId) => api.post(`/users/api/bots/${botId}/activate/`),
  archiveBot: (botId) => api.post(`/users/api/bots/${botId}/archive/`),

};