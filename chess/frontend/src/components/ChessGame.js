import React from 'react';
import { Chessboard } from 'react-chessboard';
import { Box, Paper, Typography, Button } from '@mui/material';
import { Delete } from '@mui/icons-material';

const ChessGame = ({ game, onDrop, removeBot }) => {
  return (
    <Paper elevation={3} sx={{ p: 2, mb: 3, width: '100%', maxWidth: 600 }}>
      {game.filename && (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography>Current Bot: {game.filename}</Typography>
          <Button variant="outlined" color="error" onClick={removeBot} startIcon={<Delete />}>
            Remove Bot
          </Button>
        </Box>
      )}
      {game.gameOver && (
        <Typography color="error" sx={{ mt: 1, fontWeight: 'bold' }}>
          Game Over! Result: {game.result}
        </Typography>
      )}
      <Box sx={{ width: '100%', maxWidth: 600 }}>
        <Chessboard
          position={game.position}
          onPieceDrop={onDrop}
          boardWidth={600}
          customDarkSquareStyle={{ backgroundColor: '#779556' }}
          customLightSquareStyle={{ backgroundColor: '#edeed1' }}
        />
      </Box>
    </Paper>
  );
};

export default ChessGame;