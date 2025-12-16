import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { auctionAPI } from '../services/api';
import { formatCurrency, formatDateTime, getStatusColor } from '../utils/formatters';
import Loading from '../components/Loading';
import './Auction.css';

const MyAuctions = () => {
  const [auctions, setAuctions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchMyAuctions();
  }, []);

  const fetchMyAuctions = async () => {
    try {
      const result = await auctionAPI.getMyAuctions();

      if (result.ok) {
        setAuctions(result.data || []);
      } else {
        setError('Failed to load your auctions.');
      }
    } catch (err) {
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewAuction = (auctionId) => {
    navigate(`/auction/${auctionId}`);
  };

  if (loading) {
    return <Loading message="Loading your auctions..." />;
  }

  return (
    <div className="auction-page">
      <div className="page-header">
        <div className="page-header-content">
          <h1>My Auctions</h1>
          <p className="page-subtitle">Auctions you have joined</p>
        </div>
        <div className="page-header-stats">
          <div className="header-stat">
            <span className="header-stat-number">{auctions.length}</span>
            <span className="header-stat-label">Joined</span>
          </div>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {auctions.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <h3>No auctions joined yet</h3>
          <p>Browse available auctions and join ones that interest you!</p>
          <button
            className="btn-primary"
            onClick={() => navigate('/auctions')}
            style={{ marginTop: '16px' }}
          >
            Browse Auctions
          </button>
        </div>
      ) : (
        <div className="auction-grid">
          {auctions.map((auction) => (
            <div
              key={auction.id}
              className="auction-card"
              onClick={() => handleViewAuction(auction.id)}
            >
              <div className="auction-image">
                {auction.image ? (
                  <img src={auction.image} alt={auction.title} />
                ) : (
                  <div className="no-image">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                      <circle cx="8.5" cy="8.5" r="1.5"/>
                      <path d="M21 15l-5-5L5 21"/>
                    </svg>
                  </div>
                )}
                <div
                  className="auction-card-status"
                  style={{ backgroundColor: getStatusColor(auction.status) }}
                >
                  {auction.status === 'started' && (
                    <span className="status-live-dot"></span>
                  )}
                  {auction.status}
                </div>
              </div>
              <div className="auction-info">
                <h3>{auction.title}</h3>
                <div className="auction-price-row">
                  <span className="price-label">
                    {auction.current_bid ? 'Current Bid' : 'Starting at'}
                  </span>
                  <span className={`price-value ${auction.current_bid ? 'has-bid' : ''}`}>
                    {formatCurrency(auction.current_bid || auction.starting_price)}
                  </span>
                </div>
                <div className="auction-meta">
                  <div className="auction-time">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                      <line x1="16" y1="2" x2="16" y2="6"/>
                      <line x1="8" y1="2" x2="8" y2="6"/>
                      <line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                    <span>{formatDateTime(auction.start_date_time)}</span>
                  </div>
                </div>
                <button className="btn-view">
                  View Auction
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyAuctions;
