import os
import time
import json
import uuid
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict

from .storage_path import STORAGE_ROOT, safe_write_bytes, safe_clear_hidden
from .crypto_engine import hash_password, verify_password

AUTH_FILE = STORAGE_ROOT / 'auth.dat'
LOCKOUT_FILE = STORAGE_ROOT / 'lockout.dat'
HMAC_SECRET = b'phantom_core_integrity_key_2026_scrypt'

active_sessions: Dict[str, datetime] = {}
SESSION_TIMEOUT = timedelta(minutes=30)

def sign_data(data: bytes) -> bytes:
    """Sign data using HMAC."""
    signature = hmac.new(HMAC_SECRET, data, hashlib.sha256).digest()
    return signature + data

def verify_data(signed_data: bytes) -> Optional[bytes]:
    """Verify HMAC signature and return original data."""
    if len(signed_data) < 32:
        return None
    signature = signed_data[:32]
    data = signed_data[32:]
    expected = hmac.new(HMAC_SECRET, data, hashlib.sha256).digest()
    if hmac.compare_digest(signature, expected):
        return data
    return None

def is_master_set() -> bool:
    """Check if the master password has been configured."""
    return AUTH_FILE.exists()

def setup_master_password(password: str) -> None:
    """Configure the initial master password."""
    if is_master_set():
        raise ValueError("Master authentication is already configured.")
    hash_hex, salt = hash_password(password)
    data = json.dumps({"hash": hash_hex, "salt": salt.hex()}).encode('utf-8')
    safe_write_bytes(AUTH_FILE, sign_data(data))
    try:
        from . import vault_manager
        vault_manager.set_active_master_key(password)
    except Exception:
        pass

def get_lockout_status() -> Optional[int]:
    """Return remaining lockout seconds or None."""
    if not LOCKOUT_FILE.exists():
        return None
    try:
        content = LOCKOUT_FILE.read_bytes()
        data = verify_data(content)
        if data is None:
            # Tampered: max lockout
            _set_lockout(10, time.time() + 3600)
            return 3600
        lockout_info = json.loads(data.decode('utf-8'))
        lockout_until = lockout_info.get("lockout_until", 0)
        remaining = int(lockout_until - time.time())
        if remaining > 0:
            return remaining
        return None
    except Exception:
        # Error or tampered, assume max lockout
        _set_lockout(10, time.time() + 3600)
        return 3600

def _get_failed_attempts() -> int:
    """Get the number of consecutive failed attempts."""
    if not LOCKOUT_FILE.exists():
        return 0
    try:
        content = LOCKOUT_FILE.read_bytes()
        data = verify_data(content)
        if data:
            return json.loads(data.decode('utf-8')).get("attempts", 0)
    except Exception:
        pass
    return 10  # tampered

def _set_lockout(attempts: int, lockout_until: float = 0) -> None:
    """Update lockout state and write to disk with signature."""
    data = json.dumps({"attempts": attempts, "lockout_until": lockout_until}).encode('utf-8')
    safe_write_bytes(LOCKOUT_FILE, sign_data(data))

def _clear_lockout() -> None:
    """Clear any lockout after a successful login."""
    if LOCKOUT_FILE.exists():
        safe_clear_hidden(LOCKOUT_FILE)
        LOCKOUT_FILE.unlink()

def verify_master_password(password: str) -> str:
    """Verify password and return a session token."""
    if not is_master_set():
        raise ValueError("Master password not set.")
    
    lockout = get_lockout_status()
    if lockout is not None:
        raise ValueError(f"SECURITY LOCKDOWN: Fierce lockout active. Try again in {lockout} seconds.")
    
    try:
        content = AUTH_FILE.read_bytes()
        data = verify_data(content)
        if not data:
            raise Exception("Auth file tampered or corrupted.")
        auth_info = json.loads(data.decode('utf-8'))
        stored_hash = auth_info["hash"]
        salt = bytes.fromhex(auth_info["salt"])
    except Exception:
        raise Exception("Failed to read auth info.")
    
    if verify_password(password, stored_hash, salt):
        _clear_lockout()
        token = str(uuid.uuid4())
        active_sessions[token] = datetime.now()
        try:
            from . import vault_manager
            vault_manager.set_active_master_key(password)
        except Exception:
            pass
        return token
    else:
        attempts = _get_failed_attempts() + 1
        lockout_until = 0
        if attempts >= 10:
            lockout_until = time.time() + 3600
            err_msg = "FIERCE LOCKDOWN TRIGGERED: 10+ failed attempts. System locked for 1 HOUR."
        elif attempts >= 5:
            lockout_until = time.time() + 900
            err_msg = "SECURITY LOCKDOWN TRIGGERED: 5 failed attempts crossed. System locked for 15 MINUTES."
        else:
            remaining = 5 - attempts
            err_msg = f"Invalid master password. {remaining} attempt(s) remaining before 15-minute system lockdown."
        
        _set_lockout(attempts, lockout_until)
        raise ValueError(err_msg)

def validate_session(token: str) -> bool:
    """Check if session is valid and refresh timeout."""
    if token in active_sessions:
        if datetime.now() - active_sessions[token] <= SESSION_TIMEOUT:
            active_sessions[token] = datetime.now()  # refresh
            return True
        else:
            del active_sessions[token]
    return False

def invalidate_session(token: str) -> None:
    """Log out a session."""
    active_sessions.pop(token, None)
