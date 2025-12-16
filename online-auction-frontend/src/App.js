import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import VerifyOtp from './pages/VerifyOtp';
import AuctionList from './pages/AuctionList';
import AuctionDetail from './pages/AuctionDetail';
import MyAuctions from './pages/MyAuctions';
import Bidding from './pages/Bidding';
import Profile from './pages/Profile';
import './App.css';

const AppRoutes = () => {
  const { authenticated, loading } = useAuth();

  if (loading) {
    return null;
  }

  return (
    <Routes>
      {/* Landing Page */}
      <Route path="/" element={<Landing />} />

      {/* Public Routes */}
      <Route
        path="/login"
        element={authenticated ? <Navigate to="/auctions" replace /> : <Login />}
      />
      <Route
        path="/register"
        element={authenticated ? <Navigate to="/auctions" replace /> : <Register />}
      />
      <Route path="/verify-otp" element={<VerifyOtp />} />

      {/* Protected Routes */}
      <Route
        path="/auctions"
        element={
          <ProtectedRoute>
            <AuctionList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/auction/:id"
        element={
          <ProtectedRoute>
            <AuctionDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/auction/:id/bidding"
        element={
          <ProtectedRoute>
            <Bidding />
          </ProtectedRoute>
        }
      />
      <Route
        path="/my-auctions"
        element={
          <ProtectedRoute>
            <MyAuctions />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        }
      />

      {/* Catch all */}
      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />
    </Routes>
  );
};

const AppContent = () => {
  const location = useLocation();
  const isLandingPage = location.pathname === '/';
  const isAuthPage = ['/login', '/register', '/verify-otp'].includes(location.pathname);

  return (
    <div className="app">
      {!isLandingPage && !isAuthPage && <Navbar />}
      <main className={`main-content ${isLandingPage ? 'landing-page' : ''}`}>
        <AppRoutes />
      </main>
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <AppContent />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
