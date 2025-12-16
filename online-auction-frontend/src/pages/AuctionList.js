import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { auctionAPI } from '../services/api';
import { formatCurrency, getTimeRemaining, getStatusColor } from '../utils/formatters';
import Loading from '../components/Loading';
import './Auction.css';

const AuctionList = () => {
  const [auctions, setAuctions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchAuctions();
  }, []);

  const fetchAuctions = async () => {
    try {
      const result = await auctionAPI.getAuctions();

      if (result.ok) {
        setAuctions(result.data || []);
      } else {
        setError('Failed to load auctions.');
      }
    } catch (err) {
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (auctionId) => {
    navigate(`/auction/${auctionId}`);
  };

  if (loading) {
    return <Loading message="Loading auctions..." />;
  }

  return (
    <div className="auction-page">
      <div className="page-header">
        <div className="page-header-content">
          <h1>Browse Auctions</h1>
          <p className="page-subtitle">Discover and bid on exclusive items</p>
        </div>
        <div className="page-header-stats">
          <div className="header-stat">
            <span className="header-stat-number">{auctions.length}</span>
            <span className="header-stat-label">Available Auctions</span>
          </div>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {auctions.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <path d="M21 15l-5-5L5 21"/>
            </svg>
          </div>
          <h3>No auctions available</h3>
          <p>Check back later for new auctions!</p>
        </div>
      ) : (
        <div className="auction-grid">
          {auctions.map((auction) => (
            <div
              key={auction.id}
              className="auction-card"
              onClick={() => handleViewDetails(auction.id)}
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
                      <circle cx="12" cy="12" r="10"/>
                      <path d="M12 6v6l4 2"/>
                    </svg>
                    <span>{getTimeRemaining(auction.start_date_time)}</span>
                  </div>
                </div>
                <button className="btn-view">
                  View Details
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

export default AuctionList;
