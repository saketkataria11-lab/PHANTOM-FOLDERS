import React, { useState, useEffect } from 'react';
import Titlebar from './components/Titlebar';
import LoginScreen from './components/LoginScreen';
import VaultList from './components/VaultList';
import FileExplorer from './components/FileExplorer';

export default function App() {
  const [screen, setScreen] = useState('login');
  const [sessionToken, setSessionToken] = useState(null);
  const [currentVault, setCurrentVault] = useState(null);
  const [isDecoy, setIsDecoy] = useState(false);

  useEffect(() => {
    let interval;
    if (sessionToken) {
      interval = setInterval(() => {
        fetch('/api/auth/status', {
          headers: { 'X-Session-Token': sessionToken }
        })
        .then(res => res.json())
        .then(data => {
          if (!data.authenticated) {
            handleLogout();
          }
        })
        .catch(() => handleLogout());
      }, 30000);
    }
    return () => clearInterval(interval);
  }, [sessionToken]);

  const handleLogin = (token) => {
    setSessionToken(token);
    setScreen('vaults');
  };

  const handleLogout = () => {
    setSessionToken(null);
    setCurrentVault(null);
    setIsDecoy(false);
    setScreen('login');
  };

  const handleOpenVault = (vault, decoyStatus) => {
    setCurrentVault(vault);
    setIsDecoy(decoyStatus);
    setScreen('explorer');
  };

  const handleLockVault = () => {
    if (currentVault && sessionToken) {
      fetch(`/api/vaults/${currentVault.id}/lock`, {
        method: 'POST',
        headers: { 'X-Session-Token': sessionToken }
      }).catch(err => console.error(err));
    }
    setCurrentVault(null);
    setIsDecoy(false);
    setScreen('vaults');
  };

  return (
    <>
      <Titlebar />
      {screen === 'login' && <LoginScreen onLogin={handleLogin} />}
      {screen === 'vaults' && (
        <VaultList 
          sessionToken={sessionToken} 
          onOpenVault={handleOpenVault}
          onLogout={handleLogout}
        />
      )}
      {screen === 'explorer' && (
        <FileExplorer 
          sessionToken={sessionToken}
          vault={currentVault}
          isDecoy={isDecoy}
          onLockVault={handleLockVault}
        />
      )}
    </>
  );
}
