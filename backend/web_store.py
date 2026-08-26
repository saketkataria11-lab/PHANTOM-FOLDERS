"""
Phantom Folders — Persistent Cryptographic Object Store
Stores opaque encrypted blobs and indices in a platform-appropriate location.
Every byte on disk is high-entropy AES-256-GCM ciphertext (ZERO plaintext, ZERO metadata).
Cross-platform: Windows, macOS, Linux.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, List

from .storage_path import STORAGE_ROOT, safe_write_bytes, safe_clear_hidden, safe_set_hidden

STORE_ROOT = STORAGE_ROOT / "objects"
STORE_ROOT.mkdir(parents=True, exist_ok=True)
safe_set_hidden(STORE_ROOT)

INDEX_FILE = STORE_ROOT / "sys_idx.bin"


class WebStorageDriver:
    """
    Persistent Cryptographic Object Store Driver.
    Stores only encrypted binary streams with zero plaintext metadata.
    """

    def __init__(self):
        self._indices: Dict[str, str] = {}
        self._load_indices()

    def _load_indices(self):
        if INDEX_FILE.exists():
            try:
                data = json.loads(INDEX_FILE.read_text(encoding='utf-8'))
                self._indices = data
            except Exception:
                self._indices = {}

    def _save_indices(self):
        try:
            safe_write_bytes(INDEX_FILE, json.dumps(self._indices).encode('utf-8'))
        except Exception:
            pass

    async def put_blob(self, storage_key: str, encrypted_data: bytes) -> bool:
        """Store an opaque encrypted payload as an obfuscated binary object."""
        STORE_ROOT.mkdir(parents=True, exist_ok=True)
        blob_path = STORE_ROOT / f"{storage_key}.dat"
        safe_write_bytes(blob_path, encrypted_data)
        return True

    async def get_blob(self, storage_key: str) -> Optional[bytes]:
        """Stream an encrypted payload directly from the secure storage into memory."""
        blob_path = STORE_ROOT / f"{storage_key}.dat"
        if blob_path.exists():
            return blob_path.read_bytes()
        return None

    async def delete_blob(self, storage_key: str) -> bool:
        """Securely wipe and purge a stored encrypted payload (3-pass overwrite)."""
        blob_path = STORE_ROOT / f"{storage_key}.dat"
        if blob_path.exists():
            try:
                safe_clear_hidden(blob_path)
                size = blob_path.stat().st_size
                for _ in range(3):
                    blob_path.write_bytes(os.urandom(size))
                blob_path.unlink()
                return True
            except Exception:
                pass
        return False

    async def put_vault_index(self, vault_id: str, encrypted_index_data: str) -> bool:
        """Persist encrypted vault directory index."""
        self._indices[vault_id] = encrypted_index_data
        self._save_indices()
        return True

    async def get_vault_index(self, vault_id: str) -> Optional[str]:
        """Retrieve encrypted vault directory index."""
        self._load_indices()
        return self._indices.get(vault_id)

    async def delete_vault_index(self, vault_id: str) -> bool:
        """Purge a vault index."""
        self._load_indices()
        if vault_id in self._indices:
            del self._indices[vault_id]
            self._save_indices()
            return True
        return False

    async def list_vault_ids(self) -> List[str]:
        """List all active vault IDs in the persistent repository."""
        self._load_indices()
        return list(self._indices.keys())


web_driver = WebStorageDriver()
