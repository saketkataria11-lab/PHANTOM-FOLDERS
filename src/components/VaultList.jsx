import React, { useState, useEffect } from 'react';
import CreateVaultModal from './CreateVaultModal';
import ContextMenu from './ContextMenu';
import StatusBar from './StatusBar';

export default function VaultList({ sessionToken, onOpenVault, onLogout }) {
  const [vaults, setVaults] = useState([]);
  const [metrics, setMetrics] = useState({
    quota_formatted: '2.00 TB',
    used_formatted: '0 B',
    free_formatted: '2.00 TB',
    used_percent: 0,
    total_files: 0,
    vault_count: 0
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [contextMenu, setContextMenu] = useState(null);
  const [promptVault, setPromptVault] = useState(null);
  const [vaultPassword, setVaultPassword] = useState('');
  const [authError, setAuthError] = useState('');

  const fetchVaultsAndMetrics = async () => {
    try {
      const [vaultsRes, metricsRes] = await Promise.all([
        fetch('/api/vaults', { headers: { 'X-Session-Token': sessionToken } }),
        fetch('/api/storage/metrics', { headers: { 'X-Session-Token': sessionToken } })
      ]);

      if (vaultsRes.status === 401) {
        onLogout();
        return;
      }

      if (vaultsRes.ok) {
        const data = await vaultsRes.json();
        setVaults(Array.isArray(data) ? data : (data.vaults || []));
      }

      if (metricsRes.ok) {
        const mdata = await metricsRes.json();
        setMetrics(mdata);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchVaultsAndMetrics();
  }, [sessionToken]);

  const handleContextMenu = (e, vault) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      vault
    });
  };

  const handleDelete = async (vaultId) => {
    if (window.confirm('Are you sure you want to delete this vault and all its encrypted contents?')) {
      try {
        await fetch(`/api/vaults/${vaultId}`, {
          method: 'DELETE',
          headers: { 'X-Session-Token': sessionToken }
        });
        fetchVaultsAndMetrics();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const handleOpenAttempt = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      const res = await fetch(`/api/vaults/${promptVault.id}/open`, {
        method: 'POST',
        headers: {
          'X-Session-Token': sessionToken,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password: vaultPassword })
      });
      
      const data = await res.json();
      if (res.ok) {
        setPromptVault(null);
        setVaultPassword('');
        onOpenVault(promptVault, data.is_decoy);
      } else {
        if (res.status === 401 && data.detail && data.detail.toLowerCase().includes('session')) {
          onLogout();
          return;
        }
        setAuthError(data.detail || data.error || 'Invalid password');
      }
    } catch (err) {
      setAuthError('Network error');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div className="explorer-toolbar">
        <div className="toolbar-left">
          <h2 style={{ fontSize: '1.2rem', color: 'var(--accent)' }}>VAULT INDEX</h2>
        </div>
        <div className="toolbar-right">
          <button className="btn btn-ghost" onClick={onLogout}>LOGOUT</button>
        </div>
      </div>

      {/* 2.0 TB Cluster Telemetry Banner */}
      <div style={{
        padding: '0.8rem 1.5rem',
        margin: '1rem 1.5rem 0.5rem 1.5rem',
        background: 'rgba(0, 229, 255, 0.05)',
        border: '1px solid rgba(0, 229, 255, 0.2)',
        borderRadius: '6px',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
          <span style={{ color: 'var(--accent)', fontWeight: 'bold', letterSpacing: '1px' }}>
            STORAGE CLUSTER TELEMETRY (2.0 TB ALLOCATED)
          </span>
          <span style={{ color: 'var(--text-secondary)' }}>
            USED: <strong style={{ color: 'var(--text-primary)' }}>{metrics.used_formatted}</strong> / {metrics.quota_formatted} ({metrics.used_percent}% USED)
          </span>
        </div>
        {/* Visual Storage Meter Bar */}
        <div style={{
          width: '100%',
          height: '6px',
          background: 'rgba(255, 255, 255, 0.08)',
          borderRadius: '3px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${Math.max(metrics.used_percent, 1.5)}%`,
            height: '100%',
            background: 'linear-gradient(90deg, #00e5ff, #00ff88)',
            boxShadow: '0 0 8px rgba(0, 229, 255, 0.5)'
          }} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          <span>FREE HEADROOM: <strong style={{ color: '#00ff88' }}>{metrics.free_formatted}</strong></span>
          <span>ACTIVE VAULTS: <strong>{vaults.length}</strong> | TOTAL OBJECTS: <strong>{metrics.total_files}</strong></span>
        </div>
      </div>

      <div className="vaults-container" style={{ flex: 1, overflowY: 'auto', padding: '1rem 1.5rem' }}>
        <div className="vault-grid">
          <div className="vault-card create-vault-btn" onClick={() => setShowCreateModal(true)}>
            <div style={{ fontSize: '2rem', color: 'var(--accent)' }}>+</div>
            <div>CREATE NEW VAULT</div>
          </div>
          
          {vaults.map(vault => (
            <div 
              key={vault.id} 
              className={`vault-card ${vault.locked ? 'locked' : 'unlocked'}`}
              onClick={() => setPromptVault(vault)}
              onContextMenu={(e) => handleContextMenu(e, vault)}
            >
              <h3 style={{ color: 'var(--accent)', marginBottom: '0.5rem' }}>{vault.name}</h3>
              <div className="meta">Files: <strong>{vault.file_count || 0}</strong></div>
              <div className="meta">Size: <strong>{vault.size_formatted || '0 B'}</strong></div>
              <div className="meta" style={{ marginTop: '0.4rem' }}>
                Status: <span style={{ color: vault.locked ? '#ffaa00' : '#00ff88' }}>{vault.locked ? 'LOCKED' : 'UNLOCKED'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {promptVault && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>DECRYPT VAULT: {promptVault.name}</h2>
            <form onSubmit={handleOpenAttempt} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <input 
                type="password" 
                className="login-input" 
                placeholder="VAULT PASSWORD" 
                value={vaultPassword}
                onChange={e => setVaultPassword(e.target.value)}
                autoFocus
                required
              />
              {authError && <div className="login-error">{authError}</div>}
              <div className="modal-actions">
                <button type="button" className="btn btn-ghost" onClick={() => setPromptVault(null)}>CANCEL</button>
                <button type="submit" className="btn btn-primary">OPEN</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showCreateModal && (
        <CreateVaultModal 
          sessionToken={sessionToken} 
          onClose={() => setShowCreateModal(false)} 
          onCreated={() => { setShowCreateModal(false); fetchVaultsAndMetrics(); }} 
        />
      )}

      {contextMenu && (
        <ContextMenu 
          x={contextMenu.x} 
          y={contextMenu.y} 
          items={[
            { label: 'Delete Vault', danger: true, onClick: () => handleDelete(contextMenu.vault.id) }
          ]}
          onClose={() => setContextMenu(null)}
        />
      )}

      <StatusBar 
        vaultName="MASTER CLUSTER" 
        fileCount={metrics.total_files} 
        totalSize={`${metrics.used_formatted} / 2.0 TB`} 
        isDecoy={false} 
      />
    </div>
  );
}
