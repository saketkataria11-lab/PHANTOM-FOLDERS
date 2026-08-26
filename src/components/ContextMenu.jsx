import React, { useEffect, useRef } from 'react';

export default function ContextMenu({ items, x, y, onClose }) {
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        onClose();
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    // Prevent default context menu from closing this immediately
    document.addEventListener('contextmenu', (e) => e.preventDefault());
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose]);

  return (
    <div 
      ref={menuRef} 
      className="context-menu" 
      style={{ top: y, left: x }}
    >
      {items.map((item, index) => (
        <div 
          key={index} 
          className={`context-menu-item ${item.danger ? 'danger' : ''}`}
          onClick={() => {
            item.onClick();
            onClose();
          }}
        >
          {item.label}
        </div>
      ))}
    </div>
  );
}
