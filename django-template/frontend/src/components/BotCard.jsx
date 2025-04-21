import React from 'react';
import { 
  Card, 
  CardContent, 
  CardActions, 
  Typography, 
  Button, 
  Chip, 
  Box, 
  IconButton, 
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import { styled } from '@mui/system';
import CodeIcon from '@mui/icons-material/Code';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { useHistory } from 'react-router-dom';
import axios from 'axios';

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.2s',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[4],
  },
}));

const StatusChip = styled(Chip)(({ theme, status }) => {
  const colors = {
    active: theme.palette.success.main,
    inactive: theme.palette.error.main,
    testing: theme.palette.warning.main,
  };
  
  return {
    backgroundColor: colors[status] || theme.palette.primary.main,
    color: theme.palette.getContrastText(colors[status] || theme.palette.primary.main),
  };
});

const BotCard = ({ bot, onDelete, onEdit, onTest }) => {
  const history = useHistory();
  const [anchorEl, setAnchorEl] = React.useState(null);
  
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleEdit = () => {
    handleMenuClose();
    if (onEdit) onEdit(bot);
  };
  
  const handleDelete = () => {
    handleMenuClose();
    if (onDelete) onDelete(bot.id);
  };
  
  const handleTest = () => {
    if (onTest) onTest(bot.id);
  };
  
  const handleViewDetails = () => {
    history.push(`/bots/${bot.id}`);
  };
  
  return (
    <StyledCard>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <CodeIcon color="primary" sx={{ mr: 1 }} />
            <Typography variant="h6" component="div">
              {bot.name}
            </Typography>
          </Box>
          <IconButton size="small" onClick={handleMenuOpen}>
            <MoreVertIcon />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleEdit}>
              <ListItemIcon><EditIcon fontSize="small" /></ListItemIcon>
              <ListItemText>Edit</ListItemText>
            </MenuItem>
            <MenuItem onClick={handleDelete}>
              <ListItemIcon><DeleteIcon fontSize="small" /></ListItemIcon>
              <ListItemText>Delete</ListItemText>
            </MenuItem>
          </Menu>
        </Box>
        
        <StatusChip 
          label={bot.status || 'active'} 
          status={bot.status || 'active'} 
          size="small" 
          sx={{ mb: 2 }} 
        />
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {bot.description || 'No description provided.'}
        </Typography>
        
        <Typography variant="caption" color="text.secondary" display="block">
          Last updated: {new Date(bot.updated_at || Date.now()).toLocaleDateString()}
        </Typography>
      </CardContent>
      
      <CardActions sx={{ justifyContent: 'space-between', p: 2, pt: 0 }}>
        <Button 
          size="small" 
          variant="contained" 
          color="primary"
          startIcon={<PlayArrowIcon />}
          onClick={handleTest}
        >
          Test Bot
        </Button>
        <Button 
          size="small" 
          variant="outlined"
          onClick={handleViewDetails}
        >
          Details
        </Button>
      </CardActions>
    </StyledCard>
  );
};

export default BotCard;