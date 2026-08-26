import React, { useState, useEffect, useRef } from 'react';
import ContextMenu from './ContextMenu';
import StatusBar from './StatusBar';

export default function FileExplorer({ sessionToken, vault, isDecoy, onLockVault }) {
  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState([{ id: null, name: 'root' }]);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [contextMenu, setContextMenu] = useState(null);
  const fileInputRef = useRef(null);

  const currentFolderId = currentPath[currentPath.length - 1].id;

  const fetchFiles = async () => {
    try {
      const url = `/api/vaults/${vault.id}/files?parent_id=${currentFolderId || 'root'}`;
      const res = await fetch(url, { headers: { 'X-Session-Token': sessionToken } });
      if (res.ok) {
        const data = await res.json();
        setFiles(Array.isArray(data) ? data : (data.files || []));
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchFiles();
    setSelectedIds(new Set());
  }, [currentFolderId, vault.id, sessionToken]);

  const handleFileClick = (e, fileId) => {
    e.stopPropagation();
    const newSelected = new Set(e.ctrlKey || e.metaKey ? selectedIds : []);
    if (newSelected.has(fileId)) {
      newSelected.delete(fileId);
    } else {
      newSelected.add(fileId);
    }
    setSelectedIds(newSelected);
  };

  const handleFileDoubleClick = async (file) => {
    if (file.is_folder) {
      setCurrentPath([...currentPath, { id: file.id, name: file.name }]);
    } else {
      try {
        const res = await fetch(`/api/vaults/${vault.id}/files/${file.id}/open_system`, {
          method: 'POST',
          headers: { 'X-Session-Token': sessionToken }
        });
        if (!res.ok) {
          await handleExportFile(file);
        }
      } catch (err) {
        console.error(err);
        await handleExportFile(file);
      }
    }
  };

  const handleExportFile = async (file) => {
    try {
      const res = await fetch(`/api/vaults/${vault.id}/files/${file.id}/data`, {
        headers: { 'X-Session-Token': sessionToken }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.name;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleNavigateUp = () => {
    if (currentPath.length > 1) {
      setCurrentPath(currentPath.slice(0, -1));
    }
  };

  const handleContextMenu = (e, file) => {
    e.preventDefault();
    e.stopPropagation();
    if (!selectedIds.has(file.id)) {
      setSelectedIds(new Set([file.id]));
    }
    setContextMenu({ x: e.clientX, y: e.clientY, file });
  };

  const handleNewFolder = async () => {
    const name = prompt('Folder name:');
    if (name) {
      try {
        await fetch(`/api/vaults/${vault.id}/files/folder`, {
          method: 'POST',
          headers: { 'X-Session-Token': sessionToken, 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, parent_id: currentFolderId || 'root' })
        });
        fetchFiles();
      } catch (err) { console.error(err); }
    }
  };

  const handleImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('parent_id', currentFolderId || 'root');

    try {
      await fetch(`/api/vaults/${vault.id}/files/import`, {
        method: 'POST',
        headers: { 'X-Session-Token': sessionToken },
        body: formData
      });
      fetchFiles();
    } catch (err) { console.error(err); }
    e.target.value = null;
  };

  const handleDelete = async (fileId) => {
    if (window.confirm('Delete this item?')) {
      try {
        await fetch(`/api/vaults/${vault.id}/files/${fileId}`, {
          method: 'DELETE',
          headers: { 'X-Session-Token': sessionToken }
        });
        fetchFiles();
      } catch (err) { console.error(err); }
    }
  };

  const totalSize = files.reduce((acc, f) => acc + (f.size || 0), 0);
  const sizeFormatted = totalSize > 1024 * 1024 ? `${(totalSize / 1024 / 1024).toFixed(2)} MB` : `${Math.round(totalSize / 1024)} KB`;

  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    if (!droppedFiles.length) return;

    for (const file of droppedFiles) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('parent_id', currentFolderId || 'root');

      try {
        await fetch(`/api/vaults/${vault.id}/files/import`, {
          method: 'POST',
          headers: { 'X-Session-Token': sessionToken },
          body: formData
        });
      } catch (err) {
        console.error('Failed to import file:', file.name, err);
      }
    }
    fetchFiles();
  };

  return (
    <div 
      className={`explorer ${isDragging ? 'drag-over' : ''}`}
      onClick={() => setSelectedIds(new Set())}
      onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(true); }}
      onDragLeave={(e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(false); }}
      onDrop={handleDrop}
    >
      <div className="explorer-toolbar">
        <div className="toolbar-left">
          <button className="btn" onClick={handleNavigateUp} disabled={currentPath.length <= 1}>&lt; BACK</button>
          <div className="explorer-breadcrumb">
            {currentPath.map((p, i) => (
              <React.Fragment key={p.id || 'root'}>
                {i > 0 && <span>&gt;</span>}
                {p.name}
              </React.Fragment>
            ))}
          </div>
        </div>
        <div className="toolbar-right">
          <button className="btn" onClick={handleNewFolder}>+ FOLDER</button>
          <button className="btn" onClick={() => fileInputRef.current.click()}>IMPORT</button>
          <button className="btn btn-danger" onClick={onLockVault}>LOCK VAULT</button>
          <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleImport} />
        </div>
      </div>

      <div className="file-area">
        {files.length === 0 ? (
          <div className="empty-state">No files in this directory.</div>
        ) : (
          <div className="file-grid">
            {files.map(file => (
              <div 
                key={file.id} 
                className={`file-item ${selectedIds.has(file.id) ? 'selected' : ''}`}
                onClick={(e) => handleFileClick(e, file.id)}
                onDoubleClick={() => handleFileDoubleClick(file)}
                onContextMenu={(e) => handleContextMenu(e, file)}
              >
                <div className="file-icon">{file.is_folder ? '📁' : '📄'}</div>
                <div className="file-name">{file.name}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {contextMenu && (
        <ContextMenu 
          x={contextMenu.x} 
          y={contextMenu.y} 
          items={[
            { label: 'Open File', onClick: () => handleFileDoubleClick(contextMenu.file) },
            { label: 'Export / Download', onClick: () => handleExportFile(contextMenu.file) },
            { label: 'Delete', danger: true, onClick: () => handleDelete(contextMenu.file.id) }
          ]}
          onClose={() => setContextMenu(null)}
        />
      )}

      <StatusBar 
        vaultName={vault.name} 
        fileCount={files.length} 
        totalSize={sizeFormatted} 
        isDecoy={isDecoy} 
      />
    </div>
  );
}
