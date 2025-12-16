// Use relative URLs in production (nginx proxies to backend)
// Use full URLs in development
const isDevelopment = process.env.NODE_ENV === 'development';

export const BASE_URL = isDevelopment
  ? (process.env.REACT_APP_API_URL || 'http://127.0.0.1:9000/api')
  : '/api';

export const WEB_SOCKET_URL = isDevelopment
  ? (process.env.REACT_APP_WS_URL || 'ws://localhost:9000/ws/auction')
  : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/auction`;

export const OTP_TIMER_SECONDS = 180; // 3 minutes

export const COLORS = {
  primary: '#4CAF50',
  secondary: '#2196F3',
  error: '#F44336',
  warning: '#FF9800',
  background: '#f5f5f5',
  white: '#ffffff',
  textPrimary: '#333333',
  textSecondary: '#666666',
  border: '#dddddd',
};
