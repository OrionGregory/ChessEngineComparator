import React from 'react';

// Pure HTML fallback navbar in case Material-UI is failing
const FallbackNavbar = ({ isAuthenticated, userData, handleLogout }) => {
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      width: '100%',
      backgroundColor: '#1976d2',
      color: 'white',
      padding: '16px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
      zIndex: 1300,
      margin: 0,
      border: 'none' // Remove the red border
    }}>
      <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
        Chess Bot Arena
      </div>
      
      <div>
        {isAuthenticated ? (
          <div style={{ display: 'flex', alignItems: 'center' }}>
            {userData && (
              <span style={{ marginRight: '10px' }}>
                {userData.username || 'User'}
              </span>
            )}
            <button 
              onClick={handleLogout}
              style={{
                backgroundColor: '#9c27b0',
                color: 'white',
                border: 'none',
                padding: '8px 16px',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Logout
            </button>
          </div>
        ) : (
          <a 
            href="/login"
            style={{
              backgroundColor: '#9c27b0',
              color: 'white',
              textDecoration: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              display: 'inline-block'
            }}
          >
            Login
          </a>
        )}
      </div>
    </div>
  );
};

export default FallbackNavbar;
