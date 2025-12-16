import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AuctionWebSocket from '../services/websocket';
import { formatCurrency, getStatusColor } from '../utils/formatters';
import Loading from '../components/Loading';
import './Auction.css';

const Bidding = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const wsRef = useRef(null);

  const [auction, setAuction] = useState(null);
  const [bidAmount, setBidAmount] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    const ws = new AuctionWebSocket(id, token);
    wsRef.current = ws;

    ws.onConnect(() => {
      setConnected(true);
      setError(''); // Clear any connection errors
    });

    ws.onUpdate((data) => {
      setAuction(data);
      setLoading(false);
      setError(''); // Clear errors on successful data
    });

    ws.onError((err) => {
      setError(err);
      setSubmitting(false);
    });

    ws.onBidSuccess((message) => {
      setSuccess(message);
      setBidAmount('');
      setSubmitting(false);
      setTimeout(() => setSuccess(''), 3000);
    });

    ws.onDisconnect(() => {
      setConnected(false);
    });

    ws.connect().catch((err) => {
      console.error('WebSocket connection failed:', err);
      setError('Failed to connect to auction. Please try again.');
      setLoading(false);
    });

    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect();
      }
    };
  }, [id, navigate]);

  const handleSubmitBid = (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const amount = parseFloat(bidAmount);
    if (isNaN(amount) || amount <= 0) {
      setError('Please enter a valid bid amount.');
      return;
    }

    if (!wsRef.current || !wsRef.current.isConnected()) {
      setError('Not connected to auction. Please refresh the page.');
      return;
    }

    setSubmitting(true);

    // Send bid via WebSocket - success/error will be handled by callbacks
    const sent = wsRef.current.sendBid(amount);

    if (!sent) {
      setError('Failed to submit bid. Please try again.');
      setSubmitting(false);
    }
    // If sent successfully, keep submitting=true until we get server response
  };

  const handleBack = () => {
    navigate(`/auction/${id}`);
  };

  if (loading) {
    return <Loading message="Connecting to auction..." />;
  }

  const currentBid = auction?.last_vote?.price || auction?.starting_price;
  const currentBidder = auction?.last_vote?.user || 'No bids yet';
  const isEnded = auction?.status === 'ended';

  return (
    <div className="auction-page">
      <button className="btn-back" onClick={handleBack}>
        &larr; Back to Details
      </button>

      <div className="bidding-container">
        <div className="bidding-header">
          <h1>{auction?.title || 'Auction'}</h1>
          <div className="connection-status">
            <span className={`status-dot ${connected ? 'connected' : 'disconnected'}`}></span>
            {connected ? 'Connected' : 'Disconnected'}
          </div>
        </div>

        <div
          className="status-badge large"
          style={{ backgroundColor: getStatusColor(auction?.status) }}
        >
          {auction?.status?.charAt(0).toUpperCase() + auction?.status?.slice(1)}
        </div>

        {auction?.image && (
          <div className="bidding-image">
            <img src={auction.image} alt={auction.title} />
          </div>
        )}

        <div className="bid-info-section">
          <div className="bid-info-card">
            <h3>{auction?.last_vote ? 'Current Highest Bid' : 'Starting Price'}</h3>
            <p className="current-bid">{formatCurrency(currentBid)}</p>
          </div>

          <div className="bid-info-card">
            <h3>Highest Bidder</h3>
            <p className="bidder-email">{currentBidder}</p>
          </div>

          {auction?.last_vote && (
            <div className="bid-info-card">
              <h3>Starting Price</h3>
              <p>{formatCurrency(auction?.starting_price)}</p>
            </div>
          )}
        </div>

        {error && <div className="error-banner">{error}</div>}
        {success && <div className="success-banner">{success}</div>}

        {!isEnded ? (
          <form onSubmit={handleSubmitBid} className="bid-form">
            <div className="form-group">
              <label htmlFor="bidAmount">Your Bid Amount ($)</label>
              <input
                type="number"
                id="bidAmount"
                value={bidAmount}
                onChange={(e) => setBidAmount(e.target.value)}
                placeholder={`Enter amount higher than ${formatCurrency(currentBid)}`}
                step="0.01"
                min="0"
                required
              />
            </div>

            <button
              type="submit"
              className="btn-primary btn-bid"
              disabled={submitting || !connected}
            >
              {submitting ? 'Submitting...' : 'Submit Bid'}
            </button>
          </form>
        ) : (
          <div className="auction-ended-message">
            <h2>Auction Has Ended</h2>
            <p>Final bid: {formatCurrency(currentBid)}</p>
            <p>Winner: {currentBidder}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Bidding;
