import React, { useState } from 'react';

export default function CreateVaultModal({ sessionToken, onClose, onCreated }) {
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [enableDecoy, setEnableDecoy] = useState(false);
  const [decoyPassword, setDecoyPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (enableDecoy && password === decoyPassword) {
      setError('Decoy password must be different from actual password');
      return;
    }

    try {
      const res = await fetch('/api/vaults', {
        method: 'POST',
        headers: {
          'X-Session-Token': sessionToken,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name,
          password,
          decoy_password: enableDecoy ? decoyPassword : null
        })
      });

      if (res.ok) {
        onCreated();
      } else {
        const data = await res.json();
        setError(data.detail || data.error || 'Failed to create vault');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>CREATE NEW VAULT</h2>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <input 
            type="text" 
            className="login-input" 
            placeholder="VAULT NAME" 
            value={name}
            onChange={e => setName(e.target.value)}
            required
            autoFocus
          />
          <input 
            type="password" 
            className="login-input" 
            placeholder="VAULT PASSWORD" 
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
          />
          <input 
            type="password" 
            className="login-input" 
            placeholder="CONFIRM PASSWORD" 
            value={confirmPassword}
            onChange={e => setConfirmPassword(e.target.value)}
            required
          />
          
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', marginTop: '1rem' }}>
            <input 
              type="checkbox" 
              checked={enableDecoy}
              onChange={e => setEnableDecoy(e.target.checked)}
            />
            <span style={{ color: 'var(--text-primary)', fontSize: '0.9rem' }}>ENABLE DECOY MODE</span>
          </label>

          {enableDecoy && (
            <input 
              type="password" 
              className="login-input" 
              placeholder="DECOY PASSWORD" 
              value={decoyPassword}
              onChange={e => setDecoyPassword(e.target.value)}
              required={enableDecoy}
            />
          )}

          {error && <div className="login-error">{error}</div>}

          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" onClick={onClose}>CANCEL</button>
            <button type="submit" className="btn btn-primary">CREATE</button>
          </div>
        </form>
      </div>
    </div>
  );
}
