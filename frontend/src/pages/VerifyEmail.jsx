import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../api';

const VerifyEmail = () => {
  const [status, setStatus] = useState('Verifying...');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get('token');

    if (!token) {
      setStatus('Invalid verification link.');
      return;
    }

    const verify = async () => {
      try {
        await api.verifyEmail(token);
        setStatus('Email verified successfully! You can now log in.');
      } catch (err) {
        setStatus(err.response?.data?.error || 'Verification failed. Link may have expired.');
      }
    };

    verify();
  }, [location]);

  return (
    <div style={{ textAlign: 'center', marginTop: '100px' }}>
      <h2>{status}</h2>
      <button onClick={() => navigate('/login')} style={{ marginTop: '20px', padding: '10px 20px' }}>
        Go to Login
      </button>
    </div>
  );
};

export default VerifyEmail;
