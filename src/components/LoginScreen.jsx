import React, { useState, useEffect } from 'react';

export default function LoginScreen({ onLogin }) {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isSetup, setIsSetup] = useState(false);
  const [loading, setLoading] = useState(true);
  const [lockoutSeconds, setLockoutSeconds] = useState(0);

  const checkStatus = () => {
    fetch('/api/auth/status')
      .then(res => res.json())
      .then(data => {
        setIsSetup(!data.master_set);
        setLoading(false);
      })
      .catch(() => {
        setIsSetup(false);
        setLoading(false);
      });
  };

  useEffect(() => {
    checkStatus();
  }, []);

  useEffect(() => {
    let timer;
    if (lockoutSeconds > 0) {
      timer = setInterval(() => {
        setLockoutSeconds(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            setError('');
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [lockoutSeconds]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (lockoutSeconds > 0) return;
    setError('');

    if (isSetup && password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    const endpoint = isSetup ? '/api/auth/setup' : '/api/auth/login';
    
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      });
      
      const data = await res.json();
      
      if (res.ok) {
        onLogin(data.token);
      } else {
        const errMsg = data.detail || data.error || 'Authentication failed.';
        setError(errMsg);
        // Extract lockout seconds if returned in message
        if (errMsg.includes('Try again in') || errMsg.includes('locked for')) {
          const match = errMsg.match(/(\d+)\s*(?:seconds|s|MINUTES|MINUTE|HOUR)/i);
          if (match) {
            let secs = parseInt(match[1], 10);
            if (errMsg.toUpperCase().includes('MIN')) secs *= 60;
            if (errMsg.toUpperCase().includes('HOUR')) secs *= 3600;
            setLockoutSeconds(secs);
          }
        }
      }
    } catch (err) {
      setError('Network connection error.');
    }
  };

  const formatLockout = (totalSecs) => {
    const mins = Math.floor(totalSecs / 60);
    const secs = totalSecs % 60;
    if (mins > 0) {
      return `${mins}m ${secs}s`;
    }
    return `${secs}s`;
  };

  if (loading) return <div className="login-screen" />;

  return (
    <div className="login-screen">
      <div className="login-box">
        <div>
          <h1>PHANTOM FOLDERS</h1>
          <p>ZERO-FOOTPRINT ENCRYPTED VAULT</p>
        </div>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {isSetup && (
            <p style={{ color: 'var(--accent)', fontSize: '0.9rem', letterSpacing: '1px' }}>
              INITIALIZE MASTER CIPHER KEY
            </p>
          )}
          
          <input 
            className="login-input" 
            type="password" 
            placeholder="MASTER PASSWORD" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={lockoutSeconds > 0}
            required
            autoFocus
          />
          
          {isSetup && (
            <input 
              className="login-input" 
              type="password" 
              placeholder="CONFIRM MASTER PASSWORD" 
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          )}
          
          {error && (
            <div className="login-error" style={{ textAlign: 'center', lineHeight: '1.4' }}>
              {error}
              {lockoutSeconds > 0 && (
                <div style={{ marginTop: '0.5rem', color: 'var(--danger)', fontWeight: 'bold' }}>
                  LOCKDOWN ACTIVE: {formatLockout(lockoutSeconds)}
                </div>
              )}
            </div>
          )}
          
          <button 
            className="btn btn-primary login-btn" 
            type="submit"
            disabled={lockoutSeconds > 0}
            style={{ opacity: lockoutSeconds > 0 ? 0.4 : 1 }}
          >
            {lockoutSeconds > 0 ? `LOCKED (${formatLockout(lockoutSeconds)})` : (isSetup ? 'INITIALIZE SYSTEM' : 'ACCESS VAULTS')}
          </button>
        </form>
      </div>
    </div>
  );
}
