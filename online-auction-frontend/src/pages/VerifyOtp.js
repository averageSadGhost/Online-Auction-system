import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../services/api';
import { OTP_TIMER_SECONDS } from '../config/settings';
import { formatTimer } from '../utils/formatters';
import './Auth.css';

const VerifyOtp = () => {
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [timer, setTimer] = useState(OTP_TIMER_SECONDS);
  const [canResend, setCanResend] = useState(false);

  const location = useLocation();
  const navigate = useNavigate();
  const email = location.state?.email;

  useEffect(() => {
    if (!email) {
      navigate('/login');
      return;
    }

    const interval = setInterval(() => {
      setTimer((prev) => {
        if (prev <= 1) {
          setCanResend(true);
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [email, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await authAPI.verifyOtp(email, otp);

      if (result.ok) {
        setSuccess('Email verified successfully! Redirecting to login...');
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      } else {
        setError(result.data?.error || result.data?.detail || 'Invalid OTP. Please try again.');
      }
    } catch (err) {
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await authAPI.resendOtp(email);

      if (result.ok) {
        setSuccess('OTP resent successfully!');
        setTimer(OTP_TIMER_SECONDS);
        setCanResend(false);
      } else {
        setError(result.data?.error || 'Failed to resend OTP.');
      }
    } catch (err) {
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Verify Email</h1>
        <p className="otp-info">
          We've sent a 6-digit OTP to <strong>{email}</strong>
        </p>

        <form onSubmit={handleSubmit}>
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <div className="form-group">
            <label htmlFor="otp">Enter OTP</label>
            <input
              type="text"
              id="otp"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              maxLength={6}
              required
              placeholder="Enter 6-digit OTP"
              className="otp-input"
            />
          </div>

          <div className="timer-container">
            {!canResend ? (
              <span className="timer">Time remaining: {formatTimer(timer)}</span>
            ) : (
              <span className="timer expired">OTP expired</span>
            )}
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Verifying...' : 'Verify OTP'}
          </button>

          <button
            type="button"
            className="btn-secondary"
            onClick={handleResendOtp}
            disabled={!canResend || loading}
          >
            Resend OTP
          </button>
        </form>

        <p className="auth-link">
          <Link to="/login">Back to Login</Link>
        </p>
      </div>
    </div>
  );
};

export default VerifyOtp;
