import { Box, Button, Chip, Stack, Typography } from '@mui/material';
import { History, Hub, Insights, Logout, Route } from '@mui/icons-material';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';

export default function App() {
  const navigate = useNavigate();
  const logout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <Box
        component="header"
        sx={{
          bgcolor: '#ffffff',
          borderBottom: '1px solid #d8e0dc',
          position: 'sticky',
          top: 0,
          zIndex: 5
        }}
      >
        <Stack
          direction={{ xs: 'column', md: 'row' }}
          alignItems={{ xs: 'stretch', md: 'center' }}
          justifyContent="space-between"
          gap={2}
          sx={{ px: { xs: 2, md: 4 }, py: 2 }}
        >
          <Stack direction="row" alignItems="center" gap={1.5}>
            <Box sx={{ width: 44, height: 44, borderRadius: 1.5, bgcolor: '#116466', display: 'grid', placeItems: 'center', color: '#ffffff' }}>
              <Hub />
            </Box>
            <Box>
              <Stack direction="row" gap={1} alignItems="center" flexWrap="wrap">
                <Typography variant="h6" fontWeight={900}>API Mock Console</Typography>
                <Chip size="small" label="LOCAL" sx={{ bgcolor: '#fff4df', color: '#8a4b00', fontWeight: 800 }} />
              </Stack>
              <Typography variant="caption" color="text.secondary">Endpoint builder, simulator, and request monitor</Typography>
            </Box>
          </Stack>

          <Stack direction="row" gap={1} alignItems="center" flexWrap="wrap">
            <Button startIcon={<Insights />} component={NavLink} to="/" sx={navSx}>Overview</Button>
            <Button startIcon={<Route />} component={NavLink} to="/apis" sx={navSx}>APIs</Button>
            <Button startIcon={<History />} component={NavLink} to="/logs" sx={navSx}>History</Button>
            <Button startIcon={<Logout />} onClick={logout} variant="outlined" sx={{ ml: { md: 1 }, borderColor: '#b7c7c1' }}>
              Sign out
            </Button>
          </Stack>
        </Stack>
      </Box>

      <Box sx={{ px: { xs: 2, md: 4 }, py: { xs: 2, md: 3 } }}>
        <Outlet />
      </Box>
    </Box>
  );
}

const navSx = {
  color: '#294240',
  border: '1px solid transparent',
  '&.active': {
    bgcolor: '#e0f2ee',
    color: '#0f5e61',
    borderColor: '#b9ded6'
  },
  '&:hover': {
    bgcolor: '#f1f6f4'
  }
};
