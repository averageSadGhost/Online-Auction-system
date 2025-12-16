import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { authenticated } = useAuth();
  const location = useLocation();

  if (!authenticated) return null;

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/auctions">Online Auction</Link>
      </div>
      <div className="navbar-links">
        <Link
          to="/auctions"
          className={isActive('/auctions') ? 'active' : ''}
        >
          Available Auctions
        </Link>
        <Link
          to="/my-auctions"
          className={isActive('/my-auctions') ? 'active' : ''}
        >
          My Auctions
        </Link>
        <Link
          to="/profile"
          className={isActive('/profile') ? 'active' : ''}
        >
          Profile
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
