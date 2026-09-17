import React from 'react';
import ReactDOM from 'react-dom/client';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import App from './App';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import MockApis from './pages/MockApis';
import RequestLogs from './pages/RequestLogs';
import './styles.css';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#116466' },
    secondary: { main: '#d97706' },
    background: { default: '#eef3f3', paper: '#ffffff' }
  },
  shape: { borderRadius: 8 },
  typography: {
    fontFamily: 'Inter, system-ui, Segoe UI, sans-serif'
  }
});

const router = createBrowserRouter([
  { path: '/login', element: <Login /> },
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'apis', element: <MockApis /> },
      { path: 'logs', element: <RequestLogs /> }
    ]
  }
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <RouterProvider router={router} />
    </ThemeProvider>
  </React.StrictMode>
);
