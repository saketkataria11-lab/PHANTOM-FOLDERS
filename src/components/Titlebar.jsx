import React from 'react';

export default function Titlebar() {
  const handleMinimize = () => {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.minimize();
    }
  };

  const handleMaximize = () => {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.maximize();
    }
  };

  const handleClose = () => {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.close();
    }
  };

  return (
    <div className="titlebar">
      <div className="titlebar-title">PHANTOM FOLDERS</div>
      <div className="titlebar-controls">
        <button className="titlebar-btn" onClick={handleMinimize}>─</button>
        <button className="titlebar-btn" onClick={handleMaximize}>□</button>
        <button className="titlebar-btn close" onClick={handleClose}>✕</button>
      </div>
    </div>
  );
}
