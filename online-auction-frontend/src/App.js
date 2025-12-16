import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
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

      {/* Default Route */}
      <Route
        path="/"
        element={<Navigate to={authenticated ? "/auctions" : "/login"} replace />}
      />
      <Route
        path="*"
        element={<Navigate to={authenticated ? "/auctions" : "/login"} replace />}
      />
    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Navbar />
          <main className="main-content">
            <AppRoutes />
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
