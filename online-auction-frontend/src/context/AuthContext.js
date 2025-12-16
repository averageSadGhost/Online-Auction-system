import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, isAuthenticated } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    if (isAuthenticated()) {
      try {
        const result = await authAPI.getUserInfo();
        if (result.ok) {
          setUser(result.data);
          setAuthenticated(true);
        } else {
          setAuthenticated(false);
          setUser(null);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        setAuthenticated(false);
        setUser(null);
      }
    } else {
      setAuthenticated(false);
      setUser(null);
    }
    setLoading(false);
  };

  const login = async (email, password) => {
    const result = await authAPI.login(email, password);
    if (result.ok) {
      setAuthenticated(true);
      // Fetch user info in background, don't block login
      checkAuth();
    }
    return result;
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
    setAuthenticated(false);
  };

  const value = {
    user,
    loading,
    authenticated,
    login,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
