import React, { useState, useEffect } from 'react';

export default function StatusBar({ vaultName, fileCount, totalSize, isDecoy }) {
  const [nodeInfo, setNodeInfo] = useState('LOCAL SECURE ENCLAVE');

  useEffect(() => {
    fetch('/api/system/profile')
      .then(res => res.json())
      .then(data => {
        if (data.display_name) {
          setNodeInfo(data.display_name);
        }
      })
      .catch(() => {});
  }, []);

  return (
    <div className="status-bar">
      <div className="status-item">
        <span className="status-indicator"></span>
        <span>VAULT: <strong style={{ color: 'var(--accent)' }}>{vaultName}</strong></span>
      </div>

      <div className="status-item">
        <span>STORAGE: <strong style={{ color: 'var(--success)' }}>ZERO-KNOWLEDGE CLUSTER (2.0 TB)</strong></span>
      </div>

      <div className="status-item">
        <span>NODE: <strong style={{ color: '#ffaa00' }}>{nodeInfo}</strong></span>
      </div>

      <div className="status-item">
        <span>ITEMS: <strong>{fileCount}</strong></span>
      </div>

      <div className="status-item">
        <span>SIZE: <strong>{totalSize}</strong></span>
      </div>

      {isDecoy && (
        <div className="status-item" style={{ marginLeft: 'auto', color: 'var(--accent)' }}>
          <span>DECOY PARTITION ACTIVE</span>
        </div>
      )}
    </div>
  );
}
