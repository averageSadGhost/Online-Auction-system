import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { auctionAPI } from '../services/api';
import { formatCurrency, getTimeRemaining, getStatusColor } from '../utils/formatters';
import './Landing.css';

const Landing = () => {
  const { authenticated } = useAuth();
  const navigate = useNavigate();
  const [featuredAuctions, setFeaturedAuctions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFeatured = async () => {
      try {
        const result = await auctionAPI.getAuctions();
        if (result.ok) {
          setFeaturedAuctions((result.data || []).slice(0, 3));
        }
      } catch (err) {
        console.error('Failed to fetch auctions:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchFeatured();
  }, []);

  const handleGetStarted = () => {
    navigate(authenticated ? '/auctions' : '/register');
  };

  const handleViewAuction = (id) => {
    if (authenticated) {
      navigate(`/auction/${id}`);
    } else {
      navigate('/login');
    }
  };

  return (
    <div className="landing">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-bg">
          <div className="hero-gradient"></div>
          <div className="hero-pattern"></div>
        </div>
        <div className="hero-content">
          <div className="hero-badge">Live Auctions Platform</div>
          <h1>
            Discover & Bid on
            <span className="hero-highlight"> Exclusive Items</span>
          </h1>
          <p className="hero-subtitle">
            Join thousands of bidders in real-time auctions. Find unique items,
            place your bids, and win amazing deals from the comfort of your home.
          </p>
          <div className="hero-actions">
            <button className="btn-hero-primary" onClick={handleGetStarted}>
              {authenticated ? 'Browse Auctions' : 'Get Started Free'}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </button>
            {!authenticated && (
              <Link to="/login" className="btn-hero-secondary">
                Sign In
              </Link>
            )}
          </div>
          <div className="hero-stats">
            <div className="hero-stat">
              <span className="stat-number">10K+</span>
              <span className="stat-label">Active Users</span>
            </div>
            <div className="hero-stat-divider"></div>
            <div className="hero-stat">
              <span className="stat-number">5K+</span>
              <span className="stat-label">Items Sold</span>
            </div>
            <div className="hero-stat-divider"></div>
            <div className="hero-stat">
              <span className="stat-number">99%</span>
              <span className="stat-label">Satisfaction</span>
            </div>
          </div>
        </div>
        <div className="hero-visual">
          <div className="hero-card hero-card-1">
            <div className="hero-card-image"></div>
            <div className="hero-card-info">
              <span className="hero-card-title">Vintage Watch</span>
              <span className="hero-card-bid">$2,450</span>
            </div>
          </div>
          <div className="hero-card hero-card-2">
            <div className="hero-card-image"></div>
            <div className="hero-card-info">
              <span className="hero-card-title">Art Collection</span>
              <span className="hero-card-bid">$8,900</span>
            </div>
          </div>
          <div className="hero-card hero-card-3">
            <div className="hero-card-live">LIVE</div>
            <div className="hero-card-image"></div>
            <div className="hero-card-info">
              <span className="hero-card-title">Rare Collectible</span>
              <span className="hero-card-bid">$12,500</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="features-container">
          <div className="section-header">
            <span className="section-badge">Why Choose Us</span>
            <h2>The Smarter Way to Auction</h2>
            <p>Experience the future of online auctions with our cutting-edge platform</p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              <h3>Real-Time Bidding</h3>
              <p>Experience the thrill of live auctions with instant bid updates and notifications</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
              </div>
              <h3>Secure Transactions</h3>
              <p>Your bids and payments are protected with enterprise-grade security</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </div>
              <h3>Trusted Community</h3>
              <p>Join a verified community of buyers and sellers with transparent ratings</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                  <path d="M8 21h8M12 17v4"/>
                </svg>
              </div>
              <h3>Any Device</h3>
              <p>Bid from anywhere on any device with our responsive platform</p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Auctions */}
      <section className="featured-auctions">
        <div className="featured-container">
          <div className="section-header">
            <span className="section-badge">Hot Items</span>
            <h2>Featured Auctions</h2>
            <p>Don't miss out on these trending items up for bid</p>
          </div>

          {loading ? (
            <div className="featured-loading">
              <div className="featured-skeleton"></div>
              <div className="featured-skeleton"></div>
              <div className="featured-skeleton"></div>
            </div>
          ) : featuredAuctions.length > 0 ? (
            <div className="featured-grid">
              {featuredAuctions.map((auction) => (
                <div
                  key={auction.id}
                  className="featured-card"
                  onClick={() => handleViewAuction(auction.id)}
                >
                  <div className="featured-card-image">
                    {auction.image ? (
                      <img src={auction.image} alt={auction.title} />
                    ) : (
                      <div className="featured-no-image">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                          <circle cx="8.5" cy="8.5" r="1.5"/>
                          <path d="M21 15l-5-5L5 21"/>
                        </svg>
                      </div>
                    )}
                    <div
                      className="featured-status"
                      style={{ backgroundColor: getStatusColor(auction.status) }}
                    >
                      {auction.status}
                    </div>
                  </div>
                  <div className="featured-card-content">
                    <h3>{auction.title}</h3>
                    <div className="featured-card-price">
                      <span className="price-label">
                        {auction.current_bid ? 'Current Bid' : 'Starting Price'}
                      </span>
                      <span className="price-value">
                        {formatCurrency(auction.current_bid || auction.starting_price)}
                      </span>
                    </div>
                    <div className="featured-card-time">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M12 6v6l4 2"/>
                      </svg>
                      {getTimeRemaining(auction.start_date_time)}
                    </div>
                    <button className="featured-card-btn">
                      View Auction
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M5 12h14M12 5l7 7-7 7"/>
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="featured-empty">
              <p>No auctions available at the moment. Check back soon!</p>
            </div>
          )}

          <div className="featured-cta">
            <Link to={authenticated ? "/auctions" : "/register"} className="btn-view-all">
              View All Auctions
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works">
        <div className="hiw-container">
          <div className="section-header">
            <span className="section-badge">Simple Process</span>
            <h2>How It Works</h2>
            <p>Get started in just a few simple steps</p>
          </div>
          <div className="hiw-steps">
            <div className="hiw-step">
              <div className="hiw-step-number">01</div>
              <div className="hiw-step-content">
                <h3>Create Account</h3>
                <p>Sign up for free and verify your email to get started with bidding</p>
              </div>
            </div>
            <div className="hiw-connector"></div>
            <div className="hiw-step">
              <div className="hiw-step-number">02</div>
              <div className="hiw-step-content">
                <h3>Browse & Join</h3>
                <p>Explore available auctions and join the ones that interest you</p>
              </div>
            </div>
            <div className="hiw-connector"></div>
            <div className="hiw-step">
              <div className="hiw-step-number">03</div>
              <div className="hiw-step-content">
                <h3>Place Your Bid</h3>
                <p>When the auction starts, place your bids in real-time</p>
              </div>
            </div>
            <div className="hiw-connector"></div>
            <div className="hiw-step">
              <div className="hiw-step-number">04</div>
              <div className="hiw-step-content">
                <h3>Win & Celebrate</h3>
                <p>If you have the highest bid when time runs out, you win!</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-container">
          <div className="cta-content">
            <h2>Ready to Start Bidding?</h2>
            <p>Join thousands of users who are already winning amazing deals</p>
            <div className="cta-actions">
              <button className="btn-cta-primary" onClick={handleGetStarted}>
                {authenticated ? 'Browse Auctions' : 'Create Free Account'}
              </button>
              {!authenticated && (
                <Link to="/login" className="btn-cta-secondary">
                  Already have an account? Sign in
                </Link>
              )}
            </div>
          </div>
          <div className="cta-decoration">
            <div className="cta-circle cta-circle-1"></div>
            <div className="cta-circle cta-circle-2"></div>
            <div className="cta-circle cta-circle-3"></div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-main">
            <div className="footer-brand">
              <div className="footer-logo">
                <div className="footer-logo-icon"></div>
                <span>AuctionHub</span>
              </div>
              <p>The premier online auction platform for discovering and bidding on exclusive items.</p>
            </div>
            <div className="footer-links">
              <div className="footer-column">
                <h4>Platform</h4>
                <Link to="/auctions">Browse Auctions</Link>
                <Link to="/my-auctions">My Auctions</Link>
                <Link to="/profile">My Profile</Link>
              </div>
              <div className="footer-column">
                <h4>Account</h4>
                <Link to="/login">Sign In</Link>
                <Link to="/register">Create Account</Link>
              </div>
              <div className="footer-column">
                <h4>Support</h4>
                <a href="#help">Help Center</a>
                <a href="#contact">Contact Us</a>
                <a href="#faq">FAQ</a>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 AuctionHub. All rights reserved.</p>
            <div className="footer-legal">
              <a href="#privacy">Privacy Policy</a>
              <a href="#terms">Terms of Service</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
