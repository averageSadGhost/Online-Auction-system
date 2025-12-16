import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { isAuthenticated as hasToken } from '../services/api';
import Loading from './Loading';

const ProtectedRoute = ({ children }) => {
  const { authenticated, loading } = useAuth();

  if (loading) {
    return <Loading message="Checking authentication..." />;
  }

  // Check both context state and actual token in localStorage
  if (!authenticated && !hasToken()) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
