import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { auctionAPI } from '../services/api';
import { formatCurrency, getTimeRemaining } from '../utils/formatters';
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
      <h1>Available Auctions</h1>
      <p className="page-subtitle">Browse and join auctions</p>

      {error && <div className="error-banner">{error}</div>}

      {auctions.length === 0 ? (
        <div className="empty-state">
          <p>No auctions available at the moment.</p>
          <p>Check back later for new auctions!</p>
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
                {auction.current_bid ? (
                  <p className="current-bid-info">
                    Current Bid: {formatCurrency(auction.current_bid)}
                  </p>
                ) : (
                  <p className="starting-price">
                    Starting at: {formatCurrency(auction.starting_price)}
                  </p>
                )}
                <p className="time-remaining">
                  {getTimeRemaining(auction.start_date_time)}
                </p>
                <button
                  className="btn-view"
                  onClick={() => handleViewDetails(auction.id)}
                >
                  View Details
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
