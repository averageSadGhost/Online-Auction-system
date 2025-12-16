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
      <h1>My Auctions</h1>
      <p className="page-subtitle">Auctions you have joined</p>

      {error && <div className="error-banner">{error}</div>}

      {auctions.length === 0 ? (
        <div className="empty-state">
          <p>You haven't joined any auctions yet.</p>
          <button
            className="btn-primary"
            onClick={() => navigate('/auctions')}
          >
            Browse Auctions
          </button>
        </div>
      ) : (
        <div className="auction-grid">
          {auctions.map((auction) => (
            <div key={auction.id} className="auction-card">
              <div className="auction-image">
                {auction.image ? (
                  <img src={auction.image} alt={auction.title} />
                ) : (
                  <div className="no-image">No Image</div>
                )}
              </div>
              <div className="auction-info">
                <h3>{auction.title}</h3>
                <div
                  className="status-badge small"
                  style={{ backgroundColor: getStatusColor(auction.status) }}
                >
                  {auction.status.charAt(0).toUpperCase() + auction.status.slice(1)}
                </div>
                {auction.current_bid ? (
                  <p className="current-bid-info">
                    Current Bid: {formatCurrency(auction.current_bid)}
                  </p>
                ) : (
                  <p className="starting-price">
                    Starting at: {formatCurrency(auction.starting_price)}
                  </p>
                )}
                <p className="date-info">
                  Starts: {formatDateTime(auction.start_date_time)}
                </p>
                <button
                  className="btn-view"
                  onClick={() => handleViewAuction(auction.id)}
                >
                  View Auction
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
