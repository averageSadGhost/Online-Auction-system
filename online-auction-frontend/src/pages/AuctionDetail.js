import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { auctionAPI } from '../services/api';
import { formatCurrency, formatDateTime, getStatusColor } from '../utils/formatters';
import Loading from '../components/Loading';
import './Auction.css';

const AuctionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [auction, setAuction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAuctionDetails();
  }, [id]);

  const fetchAuctionDetails = async () => {
    try {
      const result = await auctionAPI.getAuctionDetails(id);

      if (result.ok) {
        setAuction(result.data);
      } else if (result.status === 404) {
        setError('Auction not found.');
      } else {
        setError('Failed to load auction details.');
      }
    } catch (err) {
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleJoinAuction = async () => {
    setActionLoading(true);
    setError('');

    try {
      const result = await auctionAPI.joinAuction(id);

      if (result.ok) {
        fetchAuctionDetails();
      } else {
        setError(result.data?.error || 'Failed to join auction.');
      }
    } catch (err) {
      setError('Connection error. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStartBidding = () => {
    navigate(`/auction/${id}/bidding`);
  };

  const handleBack = () => {
    navigate(-1);
  };

  if (loading) {
    return <Loading message="Loading auction details..." />;
  }

  if (error && !auction) {
    return (
      <div className="auction-page">
        <div className="error-banner">{error}</div>
        <button className="btn-back" onClick={handleBack}>
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="auction-page">
      <button className="btn-back" onClick={handleBack}>
        &larr; Back
      </button>

      {error && <div className="error-banner">{error}</div>}

      <div className="auction-detail-container">
        <div className="auction-detail-image">
          {auction.image ? (
            <img src={auction.image} alt={auction.title} />
          ) : (
            <div className="no-image large">No Image Available</div>
          )}
        </div>

        <div className="auction-detail-info">
          <h1>{auction.title}</h1>

          <div className="status-badge" style={{ backgroundColor: getStatusColor(auction.status) }}>
            {auction.status.charAt(0).toUpperCase() + auction.status.slice(1)}
          </div>

          {auction.is_participant && (
            <div className="participant-badge">You are a participant</div>
          )}

          <div className="detail-section">
            <h3>Description</h3>
            <p>{auction.description || 'No description available.'}</p>
          </div>

          <div className="detail-section">
            <h3>{auction.current_bid ? 'Current Highest Bid' : 'Starting Price'}</h3>
            <p className="price">{formatCurrency(auction.current_bid || auction.starting_price)}</p>
            {auction.current_bidder && (
              <p><strong>Highest Bidder:</strong> {auction.current_bidder}</p>
            )}
          </div>

          {auction.current_bid && (
            <div className="detail-section">
              <h3>Starting Price</h3>
              <p>{formatCurrency(auction.starting_price)}</p>
            </div>
          )}

          <div className="detail-section">
            <h3>Schedule</h3>
            <p><strong>Start:</strong> {formatDateTime(auction.start_date_time)}</p>
            <p><strong>End:</strong> {formatDateTime(auction.end_date_time)}</p>
          </div>

          <div className="action-buttons">
            {!auction.is_participant && auction.status === 'scheduled' && (
              <button
                className="btn-primary"
                onClick={handleJoinAuction}
                disabled={actionLoading}
              >
                {actionLoading ? 'Joining...' : 'Join Auction'}
              </button>
            )}

            {auction.is_participant && auction.status === 'started' && (
              <button className="btn-primary" onClick={handleStartBidding}>
                Start Bidding
              </button>
            )}

            {auction.is_participant && auction.status === 'scheduled' && (
              <p className="info-text">
                Auction has not started yet. You can bid once it starts.
              </p>
            )}

            {auction.status === 'ended' && (
              <p className="info-text ended">This auction has ended.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuctionDetail;
