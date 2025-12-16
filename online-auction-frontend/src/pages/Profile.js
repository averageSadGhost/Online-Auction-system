import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Loading from '../components/Loading';
import './Profile.css';

const Profile = () => {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return <Loading message="Loading profile..." />;
  }

  if (!user) {
    return (
      <div className="profile-page">
        <div className="error-banner">Unable to load profile information.</div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="profile-card">
        <div className="profile-avatar">
          <span>{user.first_name?.charAt(0)?.toUpperCase() || 'U'}</span>
        </div>

        <h1>{user.first_name} {user.last_name}</h1>

        <div className="profile-details">
          <div className="detail-row">
            <span className="label">Email</span>
            <span className="value">{user.email}</span>
          </div>

          <div className="detail-row">
            <span className="label">Account Type</span>
            <span className="value capitalize">{user.user_type}</span>
          </div>
        </div>

        <button className="btn-logout" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  );
};

export default Profile;
